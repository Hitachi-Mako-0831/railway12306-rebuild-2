from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.passenger import Passenger
from app.schemas.passenger import PassengerCreate, PassengerUpdate

class CRUDPassenger(CRUDBase[Passenger, PassengerCreate, PassengerUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: PassengerCreate, user_id: int
    ) -> Passenger:
        db_obj = Passenger(
            user_id=user_id,
            name=obj_in.name,
            id_type=obj_in.id_type,
            id_card=obj_in.id_card,
            type=obj_in.type,
            phone=obj_in.phone,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Passenger]:
        return (
            db.query(self.model)
            .filter(Passenger.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_user_and_id_card(
        self, db: Session, *, user_id: int, id_type: int, id_card: str
    ) -> Optional[Passenger]:
        return (
            db.query(self.model)
            .filter(
                Passenger.user_id == user_id,
                Passenger.id_type == id_type,
                Passenger.id_card == id_card
            )
            .first()
        )

passenger = CRUDPassenger(Passenger)
