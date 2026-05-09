from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    event_id: str
    card_number: str = Field(min_length=16, max_length=16)
    cvv: str = Field(min_length=3, max_length=3)
    expiry_date: str


class BookingResponse(BaseModel):
    message: str
    booking_id: str


class BookingCancelResponse(BaseModel):
    message: str