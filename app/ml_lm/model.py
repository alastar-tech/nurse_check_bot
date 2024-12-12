from numpy import random as   npr

def analyse_text(text):
    npr.seed(hash(text)%256)
    return npr.choice([0,1])

#print(analyse_text("Это случайный простой текст я генерации ответа модели"))