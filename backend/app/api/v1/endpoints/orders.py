from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas import order as schemas
from app.models.order import Order, OrderItem
from app.models.enums import OrderStatus

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
    return db.query(Order).offset(skip).limit(limit).all()

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
    # 1. Calculate expiration time
    expires_at = datetime.now() + timedelta(minutes=45)
    
    # 2. Create Order
    # TODO: Get real user_id from token
    user_id = 1 
    
    order = Order(
        user_id=user_id,
        train_id=order_in.train_id,
        departure_date=order_in.departure_date,
        total_price=order_in.total_price,
        status=OrderStatus.PENDING,
        expires_at=expires_at
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # 3. Create Order Items
    for item_in in order_in.items:
        item = OrderItem(
            order_id=order.id,
            passenger_name=item_in.passenger_name,
            passenger_id_card=item_in.passenger_id_card,
            seat_type=item_in.seat_type,
            price=item_in.price,
            status=OrderStatus.PENDING
        )
        db.add(item)
    
    db.commit()
    db.refresh(order)
    return order

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
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/{order_id}/pay", response_model=schemas.Order)
def pay_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Pay order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order status is not pending")
        
    if order.expires_at and order.expires_at < datetime.now():
        order.status = OrderStatus.CANCELLED
        db.commit()
        raise HTTPException(status_code=400, detail="Order expired")

    order.status = OrderStatus.PAID
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Cancel order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatus.PENDING:
         raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/refund", response_model=schemas.Order)
def refund_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
) -> Any:
    """
    Refund order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="Only paid orders can be refunded")
        
    order.status = OrderStatus.REFUNDED
    # Update items status
    for item in order.items:
        item.status = OrderStatus.REFUNDED
        
    db.commit()
    db.refresh(order)
    return order
