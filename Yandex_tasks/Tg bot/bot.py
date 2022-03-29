import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as bs
import re

url = 'https://vc.ru/new'
TOKEN = 'THIS:IS_PRIVATE_SORRY_NOT_SORRY'
bot = telebot.TeleBot(TOKEN)

def last_article(url):
    rs = requests.get(url)
    root = bs(rs.content, 'html.parser')
    root.prettify()
    article = root.select('.content-container', limit=1)
    article = str(article)
    article = article[1:-1]
    article = re.sub('<[^>]+>', '', article)
    article = re.sub('  ', '', article)
    split_article = article.split("Статьи редакции", 1)
    massage = split_article[0]
    massage = re.sub(' Статьи редакции', '', massage)
    massage = re.sub('\n', '', massage)
    massage = massage[0:-1]
    massage += '.\nИсточник: vc.ru/new'

    return massage

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Сам-то я их не читаю, но если тебе нужно, любмиый герой, то я подскажу!')
        article = last_article(url)
        bot.send_message(call.message.chat.id, article)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Правильно! Не нужно их читать, сам начитался как-то.. и у меня все грибы повыпадали! Шучу, кончено. Не было у меня пока грибов, я еще маленький слишком.');

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет" or message.text == "привет":
        keyboard = types.InlineKeyboardMarkup() #наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes') #кнопка «Да»
        keyboard.add(key_yes) #добавляем кнопку в клавиатуру
        key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Кьюрн!\nХочешь расскажу последнюю новость с vc.ru?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

bot.polling(none_stop=True, interval=0)