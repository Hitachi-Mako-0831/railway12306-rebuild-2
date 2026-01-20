from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app import models
from app.schemas import order as schemas
from app.models.order import Order, OrderItem
from app.models.enums import OrderStatus

router = APIRouter()

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    query = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: schemas.OrderCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    expires_at = datetime.now() + timedelta(minutes=45)

    order = Order(
        user_id=current_user.id,
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
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/{order_id}/pay", response_model=schemas.Order)
def pay_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
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
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
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
    refund_in: schemas.OrderRefund,
) -> Any:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in [OrderStatus.PAID, OrderStatus.PARTIAL_REFUNDED]:
        raise HTTPException(status_code=400, detail="Only paid or partially refunded orders can be refunded")
        
    # Determine items to refund
    items_to_refund = []
    if not refund_in.order_item_ids:
        # Refund all non-refunded items
        items_to_refund = [item for item in order.items if item.status != OrderStatus.REFUNDED]
    else:
        # Verify IDs
        target_ids = set(refund_in.order_item_ids)
        for item in order.items:
            if item.id in target_ids:
                if item.status == OrderStatus.REFUNDED:
                     raise HTTPException(status_code=400, detail=f"Item {item.id} already refunded")
                items_to_refund.append(item)
        
        if len(items_to_refund) != len(target_ids):
             raise HTTPException(status_code=400, detail="Invalid order item IDs")

    if not items_to_refund:
         raise HTTPException(status_code=400, detail="No items to refund")

    # Perform Refund
    for item in items_to_refund:
        item.status = OrderStatus.REFUNDED
    
    # Update Order Status
    all_refunded = all(item.status == OrderStatus.REFUNDED for item in order.items)
    if all_refunded:
        order.status = OrderStatus.REFUNDED
    else:
        order.status = OrderStatus.PARTIAL_REFUNDED
        
    db.commit()
    db.refresh(order)
    return order
