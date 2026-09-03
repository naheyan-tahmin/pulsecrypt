from sqlalchemy.orm import Session

from ..models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username_hash(self, username_hash: str) -> User | None:
        return self.db.query(User).filter(User.username_hash == username_hash).first()

    def list_all(self) -> list[User]:
        return self.db.query(User).order_by(User.id).all()

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def save(self) -> None:
        self.db.commit()
