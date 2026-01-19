from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas import order as schemas
# from app.crud import crud_order # Will be implemented later

router = APIRouter()

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve orders.
    """
    # Placeholder
    return []

@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: schemas.OrderCreate,
    # current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new order.
    """
    # Placeholder
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    # current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get order by ID.
    """
    raise HTTPException(status_code=404, detail="Order not found")

@router.post("/{order_id}/pay", response_model=schemas.Order)
def pay_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Pay order.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Cancel order.
    """
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/{order_id}/refund", response_model=schemas.Order)
def refund_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Refund order.
    """
    raise HTTPException(status_code=501, detail="Not implemented")
