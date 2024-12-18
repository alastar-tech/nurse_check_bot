from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)


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


def custom_button(but_list,other_callbacks = []):
    if other_callbacks == []:
        other_callbacks = but_list
    elif len(but_list) != len(other_callbacks):
        raise ValueError("разная длина у списков!")
    keys = []
    for name,call in zip(but_list,other_callbacks):
        keys.append([InlineKeyboardButton(text=str(name), callback_data=str(call))])
    return InlineKeyboardMarkup(inline_keyboard=keys)