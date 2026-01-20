from typing import List, Optional
import re
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.passenger import Passenger
from app.models.user import User
from app.models.enums import IdType, VerifyStatus
from app.schemas.passenger import (
    PassengerCreate,
    PassengerUpdate,
    PATTERN_CHINESE_NAME,
    PATTERN_PASSPORT_NAME,
    PATTERN_ID_CARD_CN,
    PATTERN_PHONE_CN,
)


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
            is_default=obj_in.is_default,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, name: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[Passenger]:
        query = db.query(self.model).filter(Passenger.user_id == user_id)
        if name:
            query = query.filter(Passenger.name.ilike(f"%{name}%"))
        
        return (
            query.order_by(Passenger.is_default.desc(), Passenger.created_at.desc())
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
                Passenger.id_card == id_card,
            )
            .first()
        )

    def sync_default_for_user(self, db: Session, user: User) -> Optional[Passenger]:
        if not user:
            return None

        raw_name = (user.real_name or "").strip()
        if not raw_name:
            return None
        if not (
            re.match(PATTERN_CHINESE_NAME, raw_name)
            or re.match(PATTERN_PASSPORT_NAME, raw_name)
        ):
            return None

        raw_id_number = (user.id_number or "").strip().upper()
        raw_phone = (user.phone or "").strip()

        if not re.match(PATTERN_ID_CARD_CN, raw_id_number):
            return None
        if not re.match(PATTERN_PHONE_CN, raw_phone):
            return None

        id_type_value = IdType.ID_CARD.value
        target_id_card = raw_id_number
        target_name = raw_name

        default_passenger = (
            db.query(self.model)
            .filter(
                Passenger.user_id == user.id,
                Passenger.is_default.is_(True),
            )
            .first()
        )

        if not default_passenger:
            conflict = (
                db.query(self.model)
                .filter(
                    Passenger.user_id == user.id,
                    Passenger.id_type == id_type_value,
                    Passenger.id_card == target_id_card,
                )
                .first()
            )
            if conflict:
                conflict.is_default = True
                conflict.name = target_name
                conflict.phone = raw_phone
                conflict.verify_status = VerifyStatus.VERIFIED.value
                default_passenger = conflict
            else:
                default_passenger = Passenger(
                    user_id=user.id,
                    name=target_name,
                    id_type=id_type_value,
                    id_card=target_id_card,
                    phone=raw_phone,
                    is_default=True,
                    verify_status=VerifyStatus.VERIFIED.value,
                )
                db.add(default_passenger)
        else:
            default_passenger.name = target_name
            default_passenger.id_type = id_type_value
            default_passenger.id_card = target_id_card
            default_passenger.phone = raw_phone
            default_passenger.verify_status = VerifyStatus.VERIFIED.value

        db.commit()
        db.refresh(default_passenger)
        return default_passenger


passenger = CRUDPassenger(Passenger)
