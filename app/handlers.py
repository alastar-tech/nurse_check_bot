from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext          #для управления состояниями юзера при регистрации

import app.keyboards as kb  #импорт всех клавиатур

router = Router()           #выполняет роль диспетчера

#класс для присвоения состояний пользователю
class Reg(StatesGroup):
    reason_text = State()
    #number = State()

#обработка команды /start
@router.message(Command('start'))                 
async def cmd_start(message: Message):
    await message.answer('Это бот-помощник учета количества отработанных смен. Я буду записывать отметки о вашем присутствии в журнал.'
                         ,reply_markup=kb.main)
    await message.answer('Для того, чтобы отметиться, нажмите на кнопку ниже.')


#обработка кнопки Поставить отметку
@router.message(F.text == 'Поставить отметку')
async def check_in(message: Message):
    user_first_name = message.from_user.first_name
    await message.answer(f'{user_first_name}, здравствуйте!')
    await message.answer('Вы сегодня на работе?', reply_markup=kb.check_in_btn)  
    
    
#обработка ответа ДА
@router.callback_query(F.data == 'yes')                 
async def check_in_yes(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Рад вас видеть! Данные о присутствии я записал в журнал.')
    await callback.message.answer('Хорошей вам смены!')

#обработка ответа НЕТ
@router.callback_query(F.data == 'no')                    
async def check_in_no(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Reg.reason_text)                         ##пользователь в стостянии записи текста
    await callback.message.answer('Напишите, почему сегодня не удалось выйти?')

#ловим текст причины
@router.message(Reg.reason_text)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(reason_text=message.text)              #обновление информации о записи текста
    data = await state.get_data()                                  #созраняем текст в переменную
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    await message.answer('Мне жаль, что вам не удалось выйти на работу. Буду ждать вашего возвращения!')
    await message.answer('Информацию я передал.')
    await message.answer(f'Имя: {user_full_name}\nuser_ID:{user_id}\nПричина: {data["reason_text"]}')
    await state.clear()







#обработка введенного сбщ и ответ
@router.message(F.text)          
async def reason(message: Message):
    reason_text = message.text
    await message.answer('Мне жаль, что вам не удалось выйти на работу. Буду ждать вашего возвращения!')
    await message.answer('Информацию я передал.')
    

    

