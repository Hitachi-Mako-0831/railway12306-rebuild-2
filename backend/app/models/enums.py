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


class PassengerType(int, Enum):
    ADULT = 0
    STUDENT = 1
    CHILD = 2


class IdType(int, Enum):
    ID_CARD = 0
    PASSPORT = 1
    TAIWAN_PASS = 2
    HK_MACAU_PASS = 3


class VerifyStatus(int, Enum):
    UNVERIFIED = 0
    VERIFIED = 1

