from sqlalchemy import select, delete, update

from data.all_models import Users, Events, async_session


async def set_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.id == user_id))
        if not user:
            user = Users(id=user_id)
            session.add(user)
            await session.commit()


async def get_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.id == user_id))
        return user


async def set_event(data: dict, creator_id: int):
    async with async_session() as session:
        session.add(Events(title=data['event_name'],
                           location=data['event_location'],
                           people_count=data['event_people_count'],
                           date=data['event_date'],
                           time=data['event_time'],
                           information=data['event_information'],
                           creator_id=creator_id))
        await session.commit()


async def get_events_date():
    async with async_session() as session:
        events = await session.scalars(select(Events))
        events = [event.date for event in events]
        return set(events)


async def get_events_time(event_date: str):
    async with async_session() as session:
        events = await session.scalars(select(Events).where(Events.date == event_date))
        events = [event.time for event in events]
        return events


async def get_events(user_id: int):
    async with async_session() as session:
        events = await session.scalars(select(Events).where(Events.creator_id == user_id))
        events = [[event.title, event.id, event.date, event.time] for event in events]
        return events


async def get_event_information(event_date: str, event_time: str):
    async with async_session() as session:
        event = await session.scalar(select(Events).where(Events.date == event_date).where(Events.time == event_time))
        return event


async def accept(user_id: int, event_date: str, event_time: str):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.id == user_id))
        event = await session.scalar(select(Events).where(Events.date == event_date).where(Events.time == event_time))
        event.people_count -= 1
        if event.id in list(map(int, user.planned_events.split('/'))):
            event.planned_count -= 1
            lst = [i for i in user.planned_events.split('/')]
            lst.remove(str(event.id))
            user.planned_events = '/'.join(lst)
        if event.id in list(map(int, user.selected_events.split('/'))):
            return -1
        if event.people_count < 0:
            return 0
        user.selected_events += f'/{event.id}'
        count = event.people_count
        await session.commit()
        return count


async def maybe(user_id: int, event_date: str, event_time: str):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.id == user_id))
        event = await session.scalar(select(Events).where(Events.date == event_date).where(Events.time == event_time))
        event.planned_count += 1
        if event.id in list(map(int, user.selected_events.split('/'))):
            event.people_count += 1
            lst = [i for i in user.selected_events.split('/')]
            lst.remove(str(event.id))
            user.selected_events = '/'.join(lst)
        if event.id in list(map(int, user.planned_events.split('/'))):
            return False
        user.planned_events += f'/{event.id}'
        await session.commit()
        return True


async def decline(user_id: int, event_date: str, event_time: str):
    async with async_session() as session:
        user = await session.scalar(select(Users).where(Users.id == user_id))
        event = await session.scalar(select(Events).where(Events.date == event_date).where(Events.time == event_time))
        if event.id in list(map(int, user.planned_events.split('/'))):
            event.planned_count -= 1
            lst = [i for i in user.planned_events.split('/')]
            lst.remove(str(event.id))
            user.planned_events = '/'.join(lst)
            await session.commit()
            return True
        if event.id in list(map(int, user.selected_events.split('/'))):
            event.people_count += 1
            lst = [i for i in user.selected_events.split('/')]
            lst.remove(str(event.id))
            user.selected_events = '/'.join(lst)
            await session.commit()
            return True
        await session.commit()
        return False


async def edit(event_id: int, event_param: str, event_zn: str):
    async with (async_session() as session):
        if event_param == 'date':
            await session.execute(update(Events).where(Events.id == event_id).values(date=event_zn))
        elif event_param == 'time':
            await session.execute(update(Events).where(Events.id == event_id).values(time=event_zn))
        elif event_param == 'information':
            await session.execute(update(Events).where(Events.id == event_id).values(information=event_zn))
        elif event_param == 'location':
            await session.execute(update(Events).where(Events.id == event_id).values(location=event_zn))
        await session.commit()


async def delete_event(event_id: int):
    async with async_session() as session:
        await session.execute(delete(Events).where(Events.id == event_id))
        await session.commit()
