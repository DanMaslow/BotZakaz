from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking
from app.models.time_slot import TimeSlot

async def get_free_slots(session: AsyncSession):
    stmt = select(TimeSlot).where(TimeSlot.is_booked == False).order_by(TimeSlot.date, TimeSlot.time)
    result = await session.execute(stmt)
    return result.scalars().all()

async def book_slot(session: AsyncSession, client_id: int, slot_id: int):
    slot = await session.get(TimeSlot, slot_id)
    if not slot or slot.is_booked:
        return False
    booking = Booking(client_id=client_id, time_slot_id=slot_id)
    session.add(booking)
    slot.is_booked = True
    await session.commit()
    return True

async def get_bookings_by_client(session: AsyncSession, client_id: int):
    stmt = (
        select(Booking)
        .join(Booking.time_slot)
        .options(selectinload(Booking.time_slot))
        .where(Booking.client_id == client_id)
        .order_by(TimeSlot.date, TimeSlot.time)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def cancel_booking(session: AsyncSession, client_id: int, booking_id: int):
    booking = await session.get(Booking, booking_id)
    if not booking or booking.client_id != client_id:
        return False

    slot = await session.get(TimeSlot, booking.time_slot_id)
    if slot:
        slot.is_booked = False

    await session.delete(booking)
    await session.commit()
    return True