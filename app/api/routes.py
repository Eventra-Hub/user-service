from fastapi import APIRouter, Header, HTTPException
from datetime import datetime

from app.core.db import bookings_collection

from bson import ObjectId

from app.services.auth_client import verify_token
from app.services.event_client import (
    check_availability,
    reserve_seat,
    release_seat
)

from app.services.notification_client import (
    send_booking_confirmation,
    send_booking_cancelled
)
from app.services.payment_service import verify_payment

from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingCancelResponse
)


router = APIRouter()


@router.post(
    "/bookings",
    response_model=BookingResponse
)
async def create_booking(
    data: BookingCreate,
    authorization: str = Header(None)
):

    # 1 Verify token
    user = await verify_token(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = user.get("user_id")

    event_id = data.event_id


    # 2 Check event availability
    availability = await check_availability(event_id)

    if availability.get("seats_left", 0) <= 0:
        raise HTTPException(
            status_code=400,
            detail="Event is full"
        )

    # 3 Verify payment
    payment_valid = verify_payment(
    data.card_number,
    data.cvv,
    data.expiry_date
    )

    if not payment_valid:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed"
        )

    # 4 Reserve seat
    await reserve_seat(event_id)

    # 5 Save booking
    booking = {
        "user_id": user_id,
        "event_id": event_id,
        "status": "confirmed",
        "payment_status": "paid",
        "created_at": datetime.utcnow()
    }

    result = await bookings_collection.insert_one(booking)

    # 6 Send notification
    await send_booking_confirmation(
        user_id=user_id,
        event_id=event_id
    )

    return {
        "message": "Booking confirmed",
        "booking_id": str(result.inserted_id)
    }


@router.patch(
    "/bookings/{booking_id}/cancel",
    response_model=BookingCancelResponse
)
async def cancel_booking(
    booking_id: str,
    authorization: str = Header(None)
):

    # 1 Verify token
    user = await verify_token(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = user.get("user_id")

    # 2 Get booking
    booking = await bookings_collection.find_one({
        "_id": ObjectId(booking_id)
    })

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # 3 Check ownership
    if booking["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    # 4 Check already cancelled
    if booking["status"] == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Booking already cancelled"
        )

    # 5 Update booking status
    await bookings_collection.update_one(
        {
            "_id": ObjectId(booking_id)
        },
        {
            "$set": {
                "status": "cancelled",
                "payment_status": "refunded"
            }
        }
    )

    # 6 Release seat
    await release_seat(booking["event_id"])

    # 7 Send notification
    await send_booking_cancelled(
        user_id=user_id,
        event_id=booking["event_id"]
    )

    return {
        "message": "Booking cancelled successfully"
    }



@router.get("/bookings/me")
async def get_my_bookings(
    authorization: str = Header(None)
):

    # 1 Verify token
    user = await verify_token(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = user.get("user_id")

    # 2 Get bookings
    bookings_cursor = bookings_collection.find({
        "user_id": user_id
    })

    bookings = []

    async for booking in bookings_cursor:

        bookings.append({
            "booking_id": str(booking["_id"]),
            "event_id": booking["event_id"],
            "status": booking["status"],
            "payment_status": booking["payment_status"],
            "created_at": booking["created_at"]
        })

    return bookings 


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: str,
    authorization: str = Header(None)
):

    # 1 Verify token
    user = await verify_token(authorization)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user_id = user.get("user_id")

    # 2 Find booking
    booking = await bookings_collection.find_one({
        "_id": ObjectId(booking_id)
    })

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # 3 Check ownership
    if booking["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed"
        )

    return {
        "booking_id": str(booking["_id"]),
        "user_id": booking["user_id"],
        "event_id": booking["event_id"],
        "status": booking["status"],
        "payment_status": booking["payment_status"],
        "created_at": booking["created_at"]
    }