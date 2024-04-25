import asyncio
import time

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import keyboards as kb
import database_requests as dr
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


class AddEvent(StatesGroup):
    event_name = State()
    event_location = State()
    event_people_count = State()
    event_date = State()
    event_time = State()
    event_information = State()


class EditEvent(StatesGroup):
    edit_date = State()
    edit_time = State()
    edit_information = State()
    edit_location = State()
    event_id = State()


router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await dr.set_user(message.from_user.id)
    text = f'Привет, {message.from_user.first_name}, я бот созданный для поиска мероприятий'
    await message.answer(text, reply_markup=kb.main)


@router.message(F.text == 'Доступные мероприятия')
async def events(message: Message):
    if not await kb.dates():
        await message.answer('Мероприятий нет')
    else:
        await message.answer('Дата:', reply_markup=await kb.dates())


@router.message(F.text == 'Отменить добавление')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Добавление отменено', reply_markup=kb.main)


@router.message(F.text == 'Редактирование мероприятий')
async def edit(message: Message):
    user_id = message.from_user.id
    if not await kb.editing(user_id):
        await message.answer('Вы не создавали мероприятий')
    else:
        await message.answer('Выберите мероприятие для редактирования:', reply_markup=await kb.editing(user_id))


@router.callback_query(F.data.startswith('back_to_editing_'))
async def edit(callback: CallbackQuery):
    user_id = callback.data.split('_')[-1]
    if not await kb.editing(int(user_id)):
        await callback.message.edit_text('Вы не создавали мероприятий')
    else:
        await callback.message.edit_text('Выберите мероприятие для редактирования:',
                                         reply_markup=await kb.editing(int(user_id)))


@router.callback_query(F.data.startswith('editing_'))
async def edit(callback: CallbackQuery):
    await callback.answer('')
    event_id = int(callback.data.split('_')[1])
    event_date = callback.data.split('_')[2]
    event_time = callback.data.split('_')[3]
    event = await dr.get_event_information(event_date, event_time)
    await callback.message.edit_text(
        f'{event.title}\n\n{event.information}\n\nАдрес: {event.location}\nДата: {event.date}\nВремя: \
{event.time}\n\nСколько человек еще надо: {int(event.people_count)}\nСколько людей планирует: {event.planned_count}',
        reply_markup=await kb.edit_choose(event_id, event.creator_id))


@router.callback_query(F.data.startswith('edit_date_'))
async def edit_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новую дату:')
    event_id = callback.data.split('_')[-1]
    await state.update_data(event_id=event_id)
    await state.set_state(EditEvent.edit_date)


@router.message(EditEvent.edit_date)
async def edit_date(message: Message, state: FSMContext):
    try:
        edate = time.strptime(message.text, '%d.%m.%Y')
        await state.update_data(edit_date=message.text)
        data = await state.get_data()
        await dr.edit(data['event_id'], 'date', data['edit_date'])
        await message.answer('Вы изменили дату',
                             reply_markup=await kb.edit_choose(data['event_id'], message.from_user.id))
        await state.clear()
    except ValueError:
        await message.answer('Неправильная дата')
        await state.set_state(EditEvent.edit_date)


@router.callback_query(F.data.startswith('edit_time_'))
async def edit_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новое время:')
    event_id = callback.data.split('_')[-1]
    await state.update_data(event_id=event_id)
    await state.set_state(EditEvent.edit_time)


@router.message(EditEvent.edit_time)
async def edit_time(message: Message, state: FSMContext):
    try:
        etime = time.strptime(message.text, '%H.%M')
        await state.update_data(edit_time=message.text)
        data = await state.get_data()
        await dr.edit(data['event_id'], 'time', data['edit_time'])
        await message.answer('Вы изменили время',
                             reply_markup=await kb.edit_choose(data['event_id'], message.from_user.id))
        await state.clear()
    except ValueError:
        await message.answer('Неправильное время')
        await state.set_state(EditEvent.edit_time)


@router.callback_query(F.data.startswith('edit_information_'))
async def edit_information(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новую информацию:')
    event_id = callback.data.split('_')[-1]
    await state.update_data(event_id=event_id)
    await state.set_state(EditEvent.edit_information)


@router.message(EditEvent.edit_information)
async def edit_information(message: Message, state: FSMContext):
    await state.update_data(edit_information=message.text)
    data = await state.get_data()
    await dr.edit(data['event_id'], 'information', data['edit_information'])
    await message.answer('Вы изменили информацию',
                         reply_markup=await kb.edit_choose(data['event_id'], message.from_user.id))
    await state.clear()


@router.callback_query(F.data.startswith('edit_location_'))
async def edit_location(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новый адрес:')
    event_id = callback.data.split('_')[-1]
    await state.update_data(event_id=event_id)
    await state.set_state(EditEvent.edit_location)


@router.message(EditEvent.edit_location)
async def edit_location(message: Message, state: FSMContext):
    await state.update_data(edit_location=message.text)
    data = await state.get_data()
    await dr.edit(data['event_id'], 'location', data['edit_location'])
    await message.answer('Вы изменили адрес',
                         reply_markup=await kb.edit_choose(data['event_id'], message.from_user.id))
    await state.clear()


@router.callback_query(F.data.startswith('delete_'))
async def edit_data(callback: CallbackQuery):
    event_id = callback.data.split('_')[-1]
    await dr.delete_event(int(event_id))
    await callback.message.answer('Вы удалили мероприятие')


@router.callback_query(F.data.startswith('date_'))
async def date(callback: CallbackQuery):
    await callback.answer('')
    data = callback.data.split('_')[-1]
    if not await kb.times(data):
        await callback.message.answer('Мероприятий в этот в день нет')
    else:
        await callback.message.edit_text('Время:', reply_markup=await kb.times(data))


@router.callback_query(F.data == 'back_to_date')
async def to_dates(callback: CallbackQuery):
    await callback.message.edit_text('Доступные мероприятия', reply_markup=await kb.dates())


@router.callback_query(F.data.startswith('back_to_time_'))
async def to_times(callback: CallbackQuery):
    date = callback.data.split('_')[-1]
    await callback.message.edit_text('Время:', reply_markup=await kb.times(date))


@router.callback_query(F.data.startswith('event_'))
async def show(callback: CallbackQuery):
    await callback.answer('')
    data = callback.data.split('_')
    event = await dr.get_event_information(data[1], data[2])
    await callback.message.edit_text(
        f'{event.title}\n\n{event.information}\n\nАдрес: {event.location}\nДата: {event.date}\nВремя: \
{event.time}\n\nНеобходимо человек: {int(event.people_count)}',
        reply_markup=await kb.choose(event.date, event.time))


@router.callback_query(F.data.startswith('accept_'))
async def accept_deny(callback: CallbackQuery):
    data = callback.data.split('_')
    id = callback.from_user.id
    people_count = await dr.accept(user_id=id, event_date=data[1], event_time=data[2])
    event = await dr.get_event_information(data[1], data[2])
    creator = event.creator_id
    if people_count == -1:
        await callback.answer('Вы уже отметились')
    elif people_count == 0:
        await callback.answer('Уже набрано нужное количество')
        await bot.send_message(creator, f'Набрано нужное количество людей на мероприятие: {event.name}')
    else:
        await callback.answer('Вы успешно отметились')


@router.callback_query(F.data.startswith('maybe_'))
async def accept_deny(callback: CallbackQuery):
    data = callback.data.split('_')
    id = callback.from_user.id
    planned = await dr.maybe(user_id=id, event_date=data[1], event_time=data[2])
    if not planned:
        await callback.answer('Вы уже планируете')
    if planned:
        await callback.answer('Вы планируете')


@router.callback_query(F.data.startswith('decline_'))
async def decline(callback: CallbackQuery):
    data = callback.data.split('_')
    id = callback.from_user.id
    declined = await dr.decline(user_id=id, event_date=data[1], event_time=data[2])
    if not declined:
        await callback.answer('Вы не участвуете в этом мероприятии')
    if declined:
        await callback.answer('Вы больше не участвуете в этом мероприятии')


@router.message(F.text == 'Добавить мероприятие')
async def new_event(message: Message, state: FSMContext):
    await state.set_state(AddEvent.event_name)
    await message.answer('Введите название мероприятия:', reply_markup=kb.cancel)


@router.message(AddEvent.event_name)
async def new_event(message: Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await state.set_state(AddEvent.event_location)
    await message.answer('Введите адрес мероприятия:', reply_markup=kb.cancel)


@router.message(AddEvent.event_location)
async def new_event(message: Message, state: FSMContext):
    await state.update_data(event_location=message.text)
    await state.set_state(AddEvent.event_people_count)
    await message.answer('Введите количество требуемых участников:', reply_markup=kb.cancel)


@router.message(AddEvent.event_people_count)
async def new_event(message: Message, state: FSMContext):
    try:
        epeople = int(message.text)
        if epeople <= 0:
            await message.answer('Неправильное число', reply_markup=kb.cancel)
            await state.set_state(AddEvent.event_people_count)
        else:
            await state.update_data(event_people_count=int(message.text))
            await state.set_state(AddEvent.event_date)
            await message.answer('Введите дату в формате ДД.ММ.ГГГГ:', reply_markup=kb.cancel)
    except ValueError:
        await message.answer('Это не число', reply_markup=kb.cancel)
        await state.set_state(AddEvent.event_people_count)


@router.message(AddEvent.event_date)
async def new_event(message: Message, state: FSMContext):
    try:
        edate = time.strptime(message.text, '%d.%m.%Y')
        await state.update_data(event_date=message.text)
        await state.set_state(AddEvent.event_time)
        await message.answer('Введите время начала мероприятия в формате ЧЧ.ММ:', reply_markup=kb.cancel)
    except ValueError:
        await message.answer('Неправильная дата', reply_markup=kb.cancel)
        await state.set_state(AddEvent.event_date)


@router.message(AddEvent.event_time)
async def new_event(message: Message, state: FSMContext):
    try:
        etime = time.strptime(message.text, '%H.%M')
        await state.update_data(event_time=message.text)
        await state.set_state(AddEvent.event_information)
        await message.answer('Введите информацию о мероприятии:', reply_markup=kb.cancel)
    except ValueError:
        await message.answer('Неправильное время', reply_markup=kb.cancel)
        await state.set_state(AddEvent.event_time)


@router.message(AddEvent.event_information)
async def new_event(message: Message, state: FSMContext):
    await state.update_data(event_information=message.text)
    data = await state.get_data()
    await dr.set_event(data, creator_id=message.from_user.id)
    await message.answer(f'Мероприятие добавлено', reply_markup=kb.main)
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
