from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')  #создание БД

async_session = async_sessionmaker(engine)      #подключение к БД

#основной класс
class Base(AsyncAttrs, DeclarativeBase):
    pass

'''описание таблиц с полями'''
class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    tg_full_name = mapped_column(String(50))        #полное имя как записан в тг
    user_fname = mapped_column(String(25))          #имя при регистрации
    user_sname = mapped_column(String(25))          #отчество
    user_surname = mapped_column(String(25))        #фамилия
    user_city = mapped_column(String(50))           # город
    user_point = mapped_column(String(50))          # рабочий пункт

class Log(Base):
    __tablename__ = 'logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    date = mapped_column(String(10)) 
    time = mapped_column(String(10))
    attendance_text = mapped_column(String(50))
    attendance = mapped_column(String(10))
    
    


#создание таблиц в БД, если их нет    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)