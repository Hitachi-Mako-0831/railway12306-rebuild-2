from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Passenger])
def read_passengers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
    name: Optional[str] = None,
) -> Any:
    """
    Retrieve passengers.
    """
    passengers = crud.passenger.get_multi_by_owner(
        db=db, user_id=current_user.id, name=name, skip=skip, limit=limit
    )
    return passengers

@router.post("/", response_model=schemas.Passenger)
def create_passenger(
    *,
    db: Session = Depends(deps.get_db),
    passenger_in: schemas.PassengerCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new passenger.
    """
    # Check duplicates
    existing = crud.passenger.get_by_user_and_id_card(
        db, user_id=current_user.id, id_type=passenger_in.id_type.value, id_card=passenger_in.id_card
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Passenger with this ID card already exists for this user",
        )
    
    passenger = crud.passenger.create_with_owner(
        db=db, obj_in=passenger_in, user_id=current_user.id
    )
    return passenger

@router.put("/{id}", response_model=schemas.Passenger)
def update_passenger(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    passenger_in: schemas.PassengerUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a passenger.
    """
    passenger = crud.passenger.get(db=db, id=id)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    if passenger.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # REQ-4-3: If default passenger (self), Name and ID Card cannot be changed
    if passenger.is_default:
        if (passenger_in.name and passenger_in.name != passenger.name) or \
           (passenger_in.id_card and passenger_in.id_card != passenger.id_card) or \
           (passenger_in.id_type and passenger_in.id_type != passenger.id_type):
             raise HTTPException(
                status_code=400,
                detail="Cannot modify name or ID info for the default passenger (yourself)"
             )

    # Check duplicate if updating id_card
    if passenger_in.id_card and passenger_in.id_card != passenger.id_card:
         existing = crud.passenger.get_by_user_and_id_card(
            db, 
            user_id=current_user.id, 
            id_type=passenger_in.id_type.value if passenger_in.id_type else passenger.id_type, 
            id_card=passenger_in.id_card
        )
         if existing:
            raise HTTPException(
                status_code=400,
                detail="Passenger with this ID card already exists for this user",
            )

    passenger = crud.passenger.update(db=db, db_obj=passenger, obj_in=passenger_in)
    return passenger

@router.delete("/{id}", response_model=schemas.Passenger)
def delete_passenger(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a passenger.
    """
    passenger = crud.passenger.get(db=db, id=id)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    if passenger.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if passenger.is_default:
         raise HTTPException(status_code=400, detail="Cannot delete default passenger (yourself)")
    
    passenger = crud.passenger.remove(db=db, id=id)
    return passenger
