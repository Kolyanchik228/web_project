import sqlalchemy
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import ENGINE, ECHO

engine = create_async_engine(url=ENGINE, echo=ECHO)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True)
    created_events = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    selected_events = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    planned_events = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    events = relationship("Events", back_populates='user')


class Events(Base):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    people_count = sqlalchemy.Column(sqlalchemy.Numeric, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("users.id"))
    user = relationship('Users')
    date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    information = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    location = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    planned_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
