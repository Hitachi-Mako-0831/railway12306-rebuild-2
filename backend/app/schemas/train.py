from datetime import time
from pydantic import BaseModel, ConfigDict
from .station import Station

class TrainBase(BaseModel):
    train_number: str
    departure_time: time
    arrival_time: time
    duration_minutes: int

class Train(TrainBase):
    id: int
    from_station: Station
    to_station: Station
    
    model_config = ConfigDict(from_attributes=True)
