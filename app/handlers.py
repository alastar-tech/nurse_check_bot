from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext          #для управления состояниями юзера при регистрации
from datetime import datetime

import app.keyboards as kb          #импорт всех клавиатур
import app.database.requests as rq  #импорт запросов к БД

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
    await message.answer('Это бот-помощник учета количества отработанных смен. Я буду записывать отметки о вашем присутствии в журнал.'
                         ,reply_markup=kb.main)
    await message.answer('Чтобы отметиться нажмите на кнопку "Поставить отметку".')
    await message.answer('Если вы здесь впервые, вам необходимо зарегистрироваться.\
                         \nДля этого нажмите на кнопку "Регистрация".')

'''РЕГИСТРАЦИЯ'''
#обработка команды Регистрация
@router.message(F.text == 'Регистрация')
async def reg(message: Message):
    await message.answer('Вы хотите пройти регистрацию?', reply_markup=kb.register_check)
    
#обработка ответа "ДА - зерегистрироваться"
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



#обработка ответа "НЕТ - не зерегистрироваться"
@router.callback_query(F.data == 'reg_no')                 
async def reg_yes(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('В таком случае ждут вашу отметку.')


'''ОТМЕТКА'''
#обработка кнопки Поставить отметку
@router.message(F.text == 'Поставить отметку')
async def check_in(message: Message):
    user_first_name = message.from_user.first_name
    await message.answer(f'{user_first_name}, здравствуйте!')
    await message.answer('Вы сегодня на работе?', reply_markup=kb.check_in_btn)  
    
    
#обработка ответа "ДА - на смене"
@router.callback_query(F.data == 'check_in_yes')                 
async def check_in_yes(callback: CallbackQuery):
    await callback.answer()
    date = datetime.now().strftime("%Y-%m-%d")  #дата сообщения
    time = datetime.now().strftime("%H:%M:%S")  #время сообщения (местное время пользователя)
    tg_id = callback.from_user.id
    attendance_text = 'я на работе'
    
    attendance = 'на смене'                             #ЗАГЛУШКА ДЛЯ МОДЕЛИ!!!!
    
    await rq.log_user(tg_id, date, time, attendance_text, attendance)
    await callback.message.answer('Рад вас видеть! Данные о присутствии я записал в журнал.')
    await callback.message.answer('Хорошей вам смены!')

#обработка ответа "НЕТ - не на смене"
@router.callback_query(F.data == 'check_in_no')                    
async def check_in_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reason.reason_text)                         #пользователь в состоянии записи текста причины
    await callback.message.answer('Напишите, почему сегодня не удалось выйти?')

#ловим текст причины
@router.message(Reason.reason_text)
async def reason(message: Message, state: FSMContext):
    await state.update_data(reason_text=message.text)              #обновление информации о записи текста
    tg_id = message.from_user.id
    date = datetime.now().strftime("%Y-%m-%d")  #дата сообщения
    time = datetime.now().strftime("%H:%M:%S")  #время сообщения (местное время пользователя)
    data = await state.get_data()                       
    attendance_text = data["reason_text"]
    
    attendance = 'прочее'                        #ЗАГЛУШКА ДЛЯ МОДЕЛИ!!!
        
    await rq.log_user(tg_id, date, time, attendance_text, attendance)
    await message.answer('Мне жаль, что вам не удалось выйти на работу. Буду ждать вашего возвращения!')
    await message.answer('Информацию я передал.')
    await state.clear()
    


    

    

