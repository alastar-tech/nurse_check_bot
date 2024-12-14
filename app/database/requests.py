from app.database.models import async_session
from app.database.models import User, Log
from sqlalchemy import select


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