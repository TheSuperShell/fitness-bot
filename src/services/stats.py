from ..db.session import SessionMaker
from ..models.stats import ParamRecord


async def save_record(session_maker: SessionMaker, record: ParamRecord) -> ParamRecord:
    async with session_maker() as session:
        session.add(record)
        await session.commit()
        await session.refresh(record)
    return record
