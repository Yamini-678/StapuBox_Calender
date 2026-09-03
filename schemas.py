from typing import List , Optional , Literal
from pydantic import BaseModel , Field

class GeneratedItem(BaseModel):
    type: Literal["MCQ", "POLL"]
    sport: str
    category: str
    question: str
    options: List[str] = Field(...,min_length=2,max_length=5)
    correct_answer: Optional[str] = None

class DayBatch(BaseModel):
    date_str: str
    day_number: int
    items: List[GeneratedItem]

class WeekendBatchGeneration(BaseModel):
    days = List[DayBatch]
    