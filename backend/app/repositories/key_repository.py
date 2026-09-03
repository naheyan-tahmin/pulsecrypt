from sqlalchemy.orm import Session

from ..models.key_record import KeyRecord, DhExchange


class KeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, rec: KeyRecord) -> KeyRecord:
        self.db.add(rec)
        self.db.flush()
        return rec

    def active_for_user(self, user_id: int, key_type: str) -> KeyRecord | None:
        return (
            self.db.query(KeyRecord)
            .filter(
                KeyRecord.user_id == user_id,
                KeyRecord.key_type == key_type,
                KeyRecord.is_active == 1,
            )
            .order_by(KeyRecord.version.desc())
            .first()
        )

    def deactivate(self, rec: KeyRecord) -> None:
        rec.is_active = 0

    def add_dh(self, ex: DhExchange) -> DhExchange:
        self.db.add(ex)
        self.db.flush()
        return ex

    def get_dh(self, exchange_id: int) -> DhExchange | None:
        return self.db.get(DhExchange, exchange_id)

    def list_dh_for_user(self, user_id: int) -> list[DhExchange]:
        return (
            self.db.query(DhExchange)
            .filter((DhExchange.initiator_id == user_id) | (DhExchange.peer_id == user_id))
            .order_by(DhExchange.created_at.desc())
            .all()
        )
