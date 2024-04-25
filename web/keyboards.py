from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database_requests import get_events_date, get_events_time, get_events

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Доступные мероприятия')],
                                     [KeyboardButton(text='Добавить мероприятие')],
                                     [KeyboardButton(text='Редактирование мероприятий')]], resize_keyboard=True)

cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отменить добавление')]], resize_keyboard=True)


async def dates():
    all_dates = await get_events_date()
    if len(all_dates) == 0:
        return False

    keyboard = InlineKeyboardBuilder()
    for date in all_dates:
        keyboard.add(InlineKeyboardButton(text=f'{date}', callback_data=f'date_{date}'))

    return keyboard.adjust(3).as_markup()


async def times(date):
    all_times = await get_events_time(date)
    if len(all_times) == 0:
        return False

    keyboard = InlineKeyboardBuilder()
    for time in all_times:
        keyboard.add(InlineKeyboardButton(text=f'{time}', callback_data=f'event_{date}_{time}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'back_to_date'))

    return keyboard.adjust(3).as_markup()


async def choose(event_date, event_time):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Пойду', callback_data=f'accept_{event_date}_{event_time}'))
    keyboard.add(InlineKeyboardButton(text='Может быть', callback_data=f'maybe_{event_date}_{event_time}'))
    keyboard.add(InlineKeyboardButton(text='Отказаться', callback_data=f'decline_{event_date}_{event_time}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'back_to_time_{event_date}'))

    return keyboard.adjust(2).as_markup()


async def editing(user_id: int):
    events = await get_events(user_id)
    if len(events) == 0:
        return False

    keyboard = InlineKeyboardBuilder()
    for event in events:
        keyboard.add(InlineKeyboardButton(text=f'{event[0]}', callback_data=f'editing_{event[1]}_{event[2]}_{event[3]}'))

    return keyboard.adjust(1).as_markup()


async def edit_choose(event_id: int, creator_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f'Назад', callback_data=f'back_to_editing_{creator_id}'))
    keyboard.add(InlineKeyboardButton(text=f'Дата', callback_data=f'edit_date_{event_id}'))
    keyboard.add(InlineKeyboardButton(text=f'Время', callback_data=f'edit_time_{event_id}'))
    keyboard.add(InlineKeyboardButton(text=f'Информация', callback_data=f'edit_information_{event_id}'))
    keyboard.add(InlineKeyboardButton(text=f'Локация', callback_data=f'edit_location_{event_id}'))
    keyboard.add(InlineKeyboardButton(text=f'Удалить', callback_data=f'delete_{event_id}'))

    return keyboard.adjust(1).as_markup()
