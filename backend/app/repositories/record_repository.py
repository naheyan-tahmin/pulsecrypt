from sqlalchemy.orm import Session

from ..models.medical_record import MedicalRecord, RecordShare
from ..models.patient_profile import PatientProfile


class RecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, record: MedicalRecord) -> MedicalRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def get(self, record_id: int) -> MedicalRecord | None:
        return self.db.get(MedicalRecord, record_id)

    def list_for_owner(self, owner_id: int) -> list[MedicalRecord]:
        return (
            self.db.query(MedicalRecord)
            .filter(MedicalRecord.owner_id == owner_id)
            .order_by(MedicalRecord.updated_at.desc())
            .all()
        )

    def add_share(self, share: RecordShare) -> RecordShare:
        self.db.add(share)
        self.db.flush()
        return share

    def shares_for_recipient(self, user_id: int) -> list[RecordShare]:
        return (
            self.db.query(RecordShare)
            .filter(RecordShare.to_user_id == user_id)
            .order_by(RecordShare.created_at.desc())
            .all()
        )

    def get_profile(self, user_id: int) -> PatientProfile | None:
        return self.db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()

    def add_profile(self, profile: PatientProfile) -> PatientProfile:
        self.db.add(profile)
        self.db.flush()
        return profile
