from app.database.models import async_session
from app.database.models import User, Log
from sqlalchemy import select, text
from collections import Counter     #подсчет статистики посещаемости для файла экспорта


#запись данных о регистрации
async def reg_user(reg_date: int, 
                   tg_id: int, tg_full_name: str, user_fname: str, user_sname: str, user_surname: str,
                   user_city: str, user_company: str, user_point: str):
    async with async_session() as session:   #контекстный менеджер для открытия и зарытия сессии
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    
        if not user:
            session.add(User(reg_date=reg_date,
                             tg_id=tg_id, 
                             tg_full_name=tg_full_name,
                             user_fname=user_fname,
                             user_sname=user_sname,
                             user_surname=user_surname,
                             user_city=user_city,
                             user_company=user_company,
                             user_point=user_point))
            await session.commit()          #сохранение информации

# а есть ли юзер?
async def find_user(tg_id: int):
    async with async_session() as session:  # контекстный менеджер для открытия и зарытия сессии
        return await session.scalar(select(User).where(User.tg_id == tg_id))

#запись данных о присутствии/прочее
async def log_user(tg_id: int, date: str, time: str, attendance_text: str, attendance: str):
    async with async_session() as session:   #контекстный менеджер для открытия и зарытия сессии
        session.add(Log(tg_id=tg_id, 
                        date=date,
                        time=time,
                        attendance_text=attendance_text,
                        attendance=attendance))
        await session.commit()          #сохранение информации

#выгружаем даты
async def load_dates(year = 0):
    async with async_session() as session:  # контекстный менеджер для открытия и зарытия сессии
        if year == 0:
            req = await session.execute(select(Log.date).filter(Log.attendance=='1'))
        else:
            req = await session.execute(select(Log.date).filter(Log.attendance=='1', Log.date.like(f'{year}-%')))
        #print(req.fetchall())
        return req.fetchall()

#выгружаем логи
async def export_logs(year,month):
    async with async_session() as session:
        logs = await session.execute(text(f"SELECT * FROM logs WHERE date LIKE '{year}-{month:02d}-%' AND attendance=1"))
        idu, all_log = [], []
        for row in logs:
            idu.append(row[1])
            all_log.append(row[1:6])
        if all_log == []:
            return None, None
        users = dict()
        for id in idu:
           try:
               user = await session.execute(text(f"SELECT user_surname, user_fname, user_sname FROM users WHERE tg_id={id}"))
               users[id] = " ".join(user.fetchall()[0])
           except: users[id] = f"Неизвестен (telergam id={id})"
        new_log = [['Дата','Время','ФИО сотрудника','Сообщение']]
        count_log = []
        for row in all_log:
            new_log.append([row[1],row[2],users[row[0]],row[3]])
            count_log.append([users[row[0]],row[4]])
        counter = Counter(item[0] for item in count_log)
        count = [[key, count] for key, count in sorted(counter.items())]
        count.insert(0, ['ФИО', 'Кол-во выходов'])
        return count, new_log