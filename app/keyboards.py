from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Поставить отметку')]],
                            resize_keyboard=True)               #минимальный размер клавиатуры
                            

#инлайн клавиатура для отметки с индивидуальным колбэком
check_in_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes')],     #1й ряд
    [InlineKeyboardButton(text='Нет', callback_data='no')]      #2й ряд
])