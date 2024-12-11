import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router

bot = Bot(token=TOKEN)
dp = Dispatcher()

#отслеживание факта собщения через бесконечный запрос
async def main():   
    dp.include_router(router)       #чтобы диспетчер знал о существовании роутера, который обрабатывает хендлеры в другом файле
    await dp.start_polling(bot)         
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) #!замедляет бот на большом кол-ве пользователей, т.к. выводит лог в консоль
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

print(data)