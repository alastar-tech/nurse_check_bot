from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Поставить отметку')],
            [KeyboardButton(text='Регистрация')]],
                            resize_keyboard=True)               #минимальный размер клавиатуры

# Альтернативная клавиатура для регистрации
reg_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Регистрация', callback_data='reg_yes')]
])

#инлайн клавиатура для отметки с индивидуальным колбэком
check_in_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='check_in_yes')],     #1й ряд
    [InlineKeyboardButton(text='Нет', callback_data='check_in_no')]      #2й ряд
])

#клавиатура подтверждения процесса регистрации
register_check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='reg_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='reg_no')]
])

register_check_corr = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='reg_corr_yes')],
    [InlineKeyboardButton(text='Нет', callback_data='reg_corr_no')]
])