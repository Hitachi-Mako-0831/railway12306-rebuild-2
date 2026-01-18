from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIAL_REFUNDED = "partial_refunded"
    COMPLETED = "completed"


class SeatType(str, Enum):
    FIRST_CLASS = "first_class"
    SECOND_CLASS = "second_class"
    SOFT_SLEEPER = "soft_sleeper"
    HARD_SLEEPER = "hard_sleeper"


class TrainType(str, Enum):
    G = "G"
    D = "D"
    Z = "Z"

