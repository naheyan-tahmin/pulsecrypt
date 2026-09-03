from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.user import User
from ..models.medical_record import MedicalRecord, RecordShare
from ..repositories.record_repository import RecordRepository
from ..services.encryption_service import EncryptionService
from ..services.key_service import KeyService
from ..schemas.record_schemas import RecordCreate, RecordUpdate, RecordView, DhView
from ..core.exceptions import NotFoundError, ForbiddenError
import json


class RecordService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecordRepository(db)
        self.enc = EncryptionService(db)
        self.keys = KeyService(db)

    def _to_view(self, rec: MedicalRecord, payload: dict, shared: bool = False) -> RecordView:
        return RecordView(
            id=rec.id,
            owner_id=rec.owner_id,
            author_id=rec.author_id,
            title=payload.get("title", ""),
            body=payload.get("body", ""),
            diagnosis=payload.get("diagnosis", ""),
            created_at=rec.created_at,
            updated_at=rec.updated_at,
            shared=shared,
        )

    def create(self, actor: User, actor_role: str, data: RecordCreate) -> RecordView:
        owner_id = data.owner_id or actor.id
        if actor_role == "patient" and owner_id != actor.id:
            raise ForbiddenError("patients can only create records on their own chart")
        if actor_role == "doctor" and data.owner_id is None:
            owner_id = actor.id
        payload = {"title": data.title, "body": data.body, "diagnosis": data.diagnosis}
        ct, tag = self.enc.enc_record(owner_id, payload)
        rec = MedicalRecord(
            owner_id=owner_id,
            author_id=actor.id,
            payload_enc=ct,
            mac_tag=tag,
        )
        self.repo.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return self._to_view(rec, payload)

    def list_mine(self, actor: User) -> list[RecordView]:
        views = []
        for rec in self.repo.list_for_owner(actor.id):
            payload = self.enc.dec_record(actor.id, rec.payload_enc, rec.mac_tag)
            views.append(self._to_view(rec, payload))
        for share in self.repo.shares_for_recipient(actor.id):
            rec = self.repo.get(share.record_id)
            if not rec:
                continue
            payload = self.enc.dec_record(actor.id, share.payload_enc, share.mac_tag)
            views.append(self._to_view(rec, payload, shared=True))
        return views

    def get(self, actor: User, record_id: int) -> RecordView:
        rec = self.repo.get(record_id)
        if not rec:
            raise NotFoundError("record not found")
        if rec.owner_id == actor.id:
            payload = self.enc.dec_record(actor.id, rec.payload_enc, rec.mac_tag)
            return self._to_view(rec, payload)
        for share in self.repo.shares_for_recipient(actor.id):
            if share.record_id == record_id:
                payload = self.enc.dec_record(actor.id, share.payload_enc, share.mac_tag)
                return self._to_view(rec, payload, shared=True)
        raise ForbiddenError("no access to this record")

    def update(self, actor: User, record_id: int, data: RecordUpdate) -> RecordView:
        rec = self.repo.get(record_id)
        if not rec:
            raise NotFoundError("record not found")
        if rec.owner_id != actor.id and rec.author_id != actor.id:
            raise ForbiddenError("cannot edit this record")
        payload = self.enc.dec_record(rec.owner_id, rec.payload_enc, rec.mac_tag)
        if data.title is not None:
            payload["title"] = data.title
        if data.body is not None:
            payload["body"] = data.body
        if data.diagnosis is not None:
            payload["diagnosis"] = data.diagnosis
        ct, tag = self.enc.enc_record(rec.owner_id, payload)
        rec.payload_enc = ct
        rec.mac_tag = tag
        rec.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return self._to_view(rec, payload)

    def start_dh(self, actor: User, peer_id: int) -> DhView:
        if peer_id == actor.id:
            raise ForbiddenError("cannot open a DH channel with yourself")
        ex = self.keys.start_dh(actor.id, peer_id)
        self.db.commit()
        return self._dh_view(ex)

    def accept_dh(self, actor: User, exchange_id: int) -> DhView:
        ex = self.keys.accept_dh(exchange_id, actor.id)
        return self._dh_view(ex)

    def list_dh(self, actor: User) -> list[DhView]:
        return [self._dh_view(ex) for ex in self.keys.repo.list_dh_for_user(actor.id)]

    def share(self, actor: User, record_id: int, exchange_id: int) -> RecordView:
        rec = self.repo.get(record_id)
        if not rec:
            raise NotFoundError("record not found")
        if rec.owner_id != actor.id:
            raise ForbiddenError("only the record owner can share it")
        ex = self.keys.repo.get_dh(exchange_id)
        if not ex:
            raise NotFoundError("DH exchange not found")
        peer_id = ex.peer_id if ex.initiator_id == actor.id else ex.initiator_id
        self.keys.require_complete_dh(exchange_id, actor.id, peer_id)
        payload = self.enc.dec_record(actor.id, rec.payload_enc, rec.mac_tag)
        ct, tag = self.enc.enc_record_for(peer_id, payload)
        share = RecordShare(
            record_id=rec.id,
            from_user_id=actor.id,
            to_user_id=peer_id,
            dh_exchange_id=exchange_id,
            payload_enc=ct,
            mac_tag=tag,
        )
        self.repo.add_share(share)
        self.db.commit()
        return self._to_view(rec, payload, shared=True)

    def _dh_view(self, ex) -> DhView:
        params = json.loads(ex.params_json)
        return DhView(
            id=ex.id,
            initiator_id=ex.initiator_id,
            peer_id=ex.peer_id,
            status=ex.status,
            params=params,
            initiator_public=ex.initiator_public,
            peer_public=ex.peer_public,
            shared_secret_hash_hex=ex.shared_secret_hash.hex() if ex.shared_secret_hash else None,
        )
