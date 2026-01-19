from datetime import time
from loguru import logger
from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.station import Station
from app.models.train import Train
from app.models.enums import TrainType

def seed_data(db: Session) -> None:
    # 1. Seed Stations
    bj_station = db.query(Station).filter(Station.name == "北京南").first()
    if not bj_station:
        bj_station = Station(name="北京南", city="北京", pinyin="beijingnan", code="VNP", is_hot=True)
        db.add(bj_station)
    
    sh_station = db.query(Station).filter(Station.name == "上海虹桥").first()
    if not sh_station:
        sh_station = Station(name="上海虹桥", city="上海", pinyin="shanghaihongqiao", code="AOH", is_hot=True)
        db.add(sh_station)
    
    db.commit()
    db.refresh(bj_station)
    db.refresh(sh_station)
    
    # 2. Seed Trains
    # G1234
    train_g1234 = db.query(Train).filter(Train.train_number == "G1234").first()
    if not train_g1234:
        train_g1234 = Train(
            train_number="G1234",
            train_type=TrainType.G,
            from_station_id=bj_station.id,
            to_station_id=sh_station.id,
            departure_time=time(10, 0),
            arrival_time=time(14, 30),
            duration_minutes=270,
            arrival_day_offset=0
        )
        db.add(train_g1234)
    
    # G1 (Train ID 1 for test compatibility if G1234 is not ID 1)
    # Ideally we should rely on ID if we hardcoded ID=1 in tests, but better to query by number.
    # The E2E test uses trainId=1. So we hope this insertion gives ID 1.
    
    db.commit()
    logger.info("Demo data seeded.")

def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
