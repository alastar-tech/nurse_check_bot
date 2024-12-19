from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext          #для управления состояниями юзера при регистрации
from datetime import datetime
from io import BytesIO
from openpyxl import Workbook


import app.keyboards as kb          #импорт всех клавиатур
import app.database.requests as rq  #импорт запросов к БД
import app.ml_lm.model as mllm      #импорт работы модели ML
from config import ADMINS           #импорт списка id админов, которым нужна статистика

router = Router()                   #выполняет роль диспетчера

#состояния пользователя когда пишет текст причины
#class Reason(StatesGroup):
#    reason_text = State()
    
#состояния пользователя при регистрации
class Register(StatesGroup):
    first_name = State()
    second_name = State()
    surname = State()
    city = State()
    company = State()
    point = State()
    correct_yes = State()
    correct_no = State()

# данные для экспорта
class Export(StatesGroup):
    year = State()
    month = State()    


#обработка команды /start
@router.message(Command('start'))                 
async def cmd_start(message: Message):
    if message.chat.type == 'private':
        await message.answer('Это бот-помощник учета количества отработанных смен. Я буду записывать отметки о вашем присутствии в журнал.')
        if await rq.find_user(message.from_user.id):
            await message.answer('Все работает! Вы уже прошли регистрацию, и я готов принимать ваши сообщения в чате!')
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
async def register_fname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)                #обновление информации о регистрации
    await state.set_state(Register.city)                         #переводим в состояние регистрации фамилии
    await message.answer('Введите ваш город')

@router.message(Register.city)  
async def register_fname(message: Message, state: FSMContext):
    await state.update_data(city=message.text)               #обновление информации о регистрации
    await state.set_state(Register.company)                         #переводим в состояние регистрации фамилии
    await message.answer('Введите вашу компанию')

@router.message(Register.company)  
async def register_fname(message: Message, state: FSMContext):
    await state.update_data(company=message.text)               #обновление информации о регистрации
    await state.set_state(Register.point)                         #переводим в состояние регистрации фамилии
    await message.answer('Введите ваш объект')
    
@router.message(Register.point)  
async def register_sname(message: Message, state: FSMContext):
    await state.update_data(point=message.text)                  #обновление информации о регистрации
    reg_data = await state.get_data()
    user_fname = reg_data['first_name']
    user_sname = reg_data['second_name']
    user_surname = reg_data['surname']
    user_city = reg_data['city']                  
    user_company = reg_data['company']
    user_point = reg_data['point']
    
    await message.answer('Введенные данные:')
    await message.answer(f'имя: {user_fname}\nотчество: {user_sname}\nфамилия: {user_surname}\
                            \nгород: {user_city}\nкомпания: {user_company}\nобъект: {user_point}')
    await message.answer('Все верно?', reply_markup=kb.register_check_corr)
    await state.set_state(Register.correct_no)         #обновляем статус на случай некорректного ввода


#обработка ответа "ДА - корректно"
@router.callback_query(F.data == 'reg_corr_yes')                 
async def reg_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    reg_data = await state.get_data()               #словарь с данными
    user_fname = reg_data['first_name']
    user_sname = reg_data['second_name']
    user_surname = reg_data['surname']
    user_city = reg_data['city']             
    user_company = reg_data['company']
    user_point = reg_data['point']
    tg_id = callback.from_user.id
    tg_full_name = callback.from_user.full_name
    reg_date = datetime.now().strftime("%Y-%m-%d")  #дата регистрации
    # пишем данные в базу
    await rq.reg_user(reg_date, tg_id, tg_full_name, user_fname, user_sname, user_surname, user_city, user_company, user_point)
    await callback.message.answer('Регистрация пройдена! Буду ждать ваших сообщений в чате.')
    await state.clear()
                        
    
#обработка ответа "НЕТ - не корректно"
@router.callback_query(F.data == 'reg_corr_no', Register.correct_no)                 
async def reg_yes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer('Регистрация прервана.\nДля повтора попытки нажмите кнопку ниже.',
                                  reply_markup=kb.reg_btn)
    
    

'''Экспорт файла статистики за месяц'''
# спрашиваем год
@router.message(Command('export'))
async def export_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id in ADMINS:
        if callback.chat.type != 'private':
            await callback.answer('Я бы не рекомендовал выгружать эту информацию в общий чат!\n@nurse_check_bot')
        else:            
            dates = await rq.load_dates()
            years = sorted(list(set(datetime.strptime(date[0], "%Y-%m-%d").year for date in dates)))
            await callback.answer('Выберите год:', reply_markup=kb.custom_button(years))
            await state.set_state(Export.year)
    else:
        await callback.answer('Эта функция доступна только администраторам!')
        
# спрашиваем месяц
@router.callback_query(Export.year)
async def export_continue(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(year=callback.data)
    dates = await rq.load_dates(callback.data)
    months = sorted(list(set(datetime.strptime(date[0], "%Y-%m-%d").month for date in dates)))
    names = ['','Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    month_names = [names[m] for m in months]
    await state.set_state(Export.month)
    await callback.message.answer('Веберите месяц:', reply_markup=kb.custom_button(month_names,months))

# отвечаем файлом
@router.callback_query(Export.month)
async def export_finish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(month=callback.data)
    if callback.from_user.id in ADMINS:
        stgd = await state.get_data()
        countlog, datalog = await rq.export_logs(int(stgd['year']),int(stgd['month']))
        if (datalog == None):
            await callback.message.answer("Данные отсутствуют, возможно это связано с ошибкой. Обратитесь к разработчикам.")
        else:
            file_data = BytesIO()
            wb = Workbook()
            ws1 = wb.active
            ws1.title = "подсчет_пофамильно"
            ws2 = wb.create_sheet(title="полный_журнал")
            for row in countlog:
                ws1.append(row)
            for row in datalog:
                ws2.append(row)
            wb.save(file_data)
            file_data.seek(0)
            file_bin = BufferedInputFile(file_data.getvalue(), filename = f"Посещения_{stgd['year']}-{int(stgd['month']):02d}.xlsx")
            
            from run import bot
            m_names = ['','Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
            request_month = m_names[int(stgd['month'])] #для красивого вывода сообщения
            await callback.message.answer(f"Вот файл с отметками на рабочем месте за {str.lower(request_month)} {stgd['year']} года 👇")
            print(stgd)
            await bot.send_document(chat_id=callback.from_user.id, document=file_bin)
            
    else:
        await callback.message.answer('Эта функция доступна только администраторам! ')
        from run import bot
        await bot.send_message(chat_id=ADMINS[0], text=' Попытка взлома со стороны пользователя @'+callback.from_user.username)
    await state.clear()      
        
        
        
        
'''Скрипт отслеживания сообщений в чате'''
#если по сообщению не находит id юзера, отправляет кнопку регистрации в боте, а само сообщ НЕ отправляет в БД
@router.message()
async def any_message(message: Message):
    from run import bot
    
    #если отправили только текст
    if message.text != None:
        context = message.text #получение каждого сообщения
        
        #если юзер пишет в чате (не в боте)
        if message.chat.id != message.from_user.id:
            #если юзер не зареган
            if not await rq.find_user(message.from_user.id):
                
                await bot.send_message(chat_id = message.chat.id, 
                                    reply_to_message_id = message.message_id,
                                    text = 'Сообщение не принято. Пройдите регистрацию через бот @nurse_check_bot')
                print(message.chat.id)
                await bot.send_message(chat_id=message.from_user.id,
                                        text='Вы написали сообщение в рабочем чате. Чтобы бот мог отслеживать Ваши сообщения - \
                                        пройдите регистрацию по кнопке.',
                                        reply_markup=kb.reg_btn)
            #если юзер зареган
            else:
                #req_string = message.from_user.first_name+" "+message.from_user.last_name+" "+context
                is_onpoint, coef = mllm.analyze_text(context) # передача сообщения в модель
                if is_onpoint:
                    attendance = 1
                    await message.reply('Сообщение о присутствии принято.')
                else:
                    attendance = 0
                tg_id = message.from_user.id
                date = datetime.now().strftime("%Y-%m-%d")  #дата сообщения
                time = datetime.now().strftime("%H:%M:%S")  #время сообщения (местное время пользователя)
                await rq.log_user(tg_id, date, time, context, attendance, float(coef[0][1]))
        
        #если юзер написал в боте
        else:
            await message.reply('Тут я не принимаю сообщения - только в чате :)')


    

    

