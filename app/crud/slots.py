from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.time_slot import TimeSlot
from datetime import date, time

async def create_time_slot(session: AsyncSession, slot_date: date, slot_time: time) -> None:
    stmt = select(TimeSlot).where(
        and_(TimeSlot.date == slot_date, TimeSlot.time == slot_time)
    )
    result = await session.execute(stmt)
    existing_slot = result.scalars().first()
    if existing_slot:
        # Слот уже есть, не создаём дубликат
        return
    new_slot = TimeSlot(date=slot_date, time=slot_time, is_booked=False)
    session.add(new_slot)
    await session.commit()

async def get_slots_by_date(session: AsyncSession, slot_date: date):
    stmt = (
        select(TimeSlot)
        .where(TimeSlot.date == slot_date)
        .order_by(TimeSlot.time)
    )
    result = await session.execute(stmt)
    return result.scalars().all()