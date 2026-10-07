from enum import Enum


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class BUCClassification(Enum):
    BILL = "bill"
    USAGE = "usage"
    CHOICE = "choice"


class ReflectiveContext(Enum):
    NEED = "need"
    LOVE = "love"
    LIKE = "like"
    WANT = "want"


class ExpenseCategory(Enum):
    TRANSPORT = "Transport"
    ACCOMMODATION = "Accommodation"
    FOOD = "Food"
    ACTIVITIES = "Activities"
    OTHER = "Other"
