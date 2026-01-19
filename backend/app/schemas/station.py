from pydantic import BaseModel, ConfigDict

class StationBase(BaseModel):
    name: str
    city: str

class Station(StationBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
