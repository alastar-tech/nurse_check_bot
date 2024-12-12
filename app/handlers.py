from aiogram import F, Router, Bot, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext          #для управления состояниями юзера при регистрации
from datetime import datetime

import app.keyboards as kb          #импорт всех клавиатур
import app.database.requests as rq  #импорт запросов к БД
import app.ml_lm.model as mllm

router = Router()           #выполняет роль диспетчера

#состояния пользователя когда пишет текст причины
class Reason(StatesGroup):
    reason_text = State()
    
#состояния пользователя при регистрации
class Register(StatesGroup):
    first_name = State()
    second_name = State()
    surname = State()
    correct_yes = State()
    correct_no = State()
    

#обработка команды /start
@router.message(Command('start'))                 
async def cmd_start(message: Message):
    if message.chat.type == 'private':
        await message.answer('Это бот-помощник учета количества отработанных смен. Я буду записывать отметки о вашем присутствии в журнал.')
        if(rq.find_user(message.from_user.id)):
            await message.answer( 'Вы проходили регистрацию ранее!')
        else:
            await message.answer('Вам необходимо зарегистрироваться!', reply_markup=kb.reg_btn)

'''РЕГИСТРАЦИЯ'''
@router.callback_query(F.data == 'reg_yes')                 
async def reg_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Register.first_name)              #переводим в состояние регистрации имени
    await callback.message.answer('Введите ваше имя')

@router.message(Register.first_name)  
async def register_fname(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)                #обновление информации о регистрации
    await state.set_state(Register.second_name)                     #переводим в состояние регистрации фамилии
    await message.answer('Введите ваше отчество')

@router.message(Register.second_name)  
async def register_fname(message: Message, state: FSMContext):
    await state.update_data(second_name=message.text)               #обновление информации о регистрации
    await state.set_state(Register.surname)                         #переводим в состояние регистрации фамилии
    await message.answer('Введите вашу фамилию')

@router.message(Register.surname)  
async def register_sname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)                  #обновление информации о регистрации
    reg_data = await state.get_data()
    user_fname = reg_data['first_name']
    user_sname = reg_data['second_name']
    user_surname = reg_data['surname']
    await message.answer('Введенные данные:')
    await message.answer(f'имя: {user_fname}\nотчество: {user_sname}\nфамилия: {user_surname}')
    await message.answer('Все верно?', reply_markup=kb.register_check_corr)
    await state.set_state(Register.correct_no)      #обновляем статус на случай некорректного ввода


#обработка ответа "ДА - корректно"
@router.callback_query(F.data == 'reg_corr_yes')                 
async def reg_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    reg_data = await state.get_data()               #словарь с данными
    user_fname = reg_data['first_name']
    user_sname = reg_data['second_name']
    user_surname = reg_data['surname']
    tg_id = callback.from_user.id
    tg_full_name = callback.from_user.full_name
    # пишем данные в базу
    await rq.reg_user(tg_id, tg_full_name, user_fname, user_sname, user_surname)
    await callback.message.answer('Регистрация пройдена! Буду ждать вашей отметки.')
    await state.clear()
                        
    
#обработка ответа "НЕТ - не корректно"
@router.callback_query(F.data == 'reg_corr_no', Register.correct_no)                 
async def reg_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    reg_data['first_name']
    await state.clear()
    await callback.message.answer('Регистрация прервана.\nДля повтора попытки нажмите кнопку "Регистрация".')


'''Скрипт отслеживания сообщений в чате'''
@router.message()
async def any_message(message: Message):
    context = message.text             #получение каждого сообщения
    if (not await rq.find_user(message.from_user.id)):
        from run import bot
        await bot.send_message(chat_id=message.from_user.id,text='Вы написали сообщение в рабочем чате. Чтобы бот мог отслеживать Ваши сообщения, Вам необходимо зарегистрироваться!!', reply_markup=kb.reg_btn)
    is_onpoint = mllm.analyse_text(context) # передача сообщения в модель
    if is_onpoint:
        attendance = 1
        await message.reply('Принял сообщение о Вашем прибытии')
    else:
        attendance = 0
    tg_id = message.from_user.id
    date = datetime.now().strftime("%Y-%m-%d")  #дата сообщения
    time = datetime.now().strftime("%H:%M:%S")  #время сообщения (местное время пользователя)
    await rq.log_user(tg_id, date, time, context, attendance)


    


    

    

