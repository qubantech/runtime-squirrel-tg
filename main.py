import math
import random
from datetime import datetime

import telebot
from telebot import types
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd


def newNotifications(event):
    print(db.reference("/bot/notification").get())
    notifications = db.reference("/bot/notification").get()
    if notifications:
        notifications = dict(notifications)
        for el in notifications:
            if el == "empty":
                continue
            print("elems:")
            print(notifications[el])
            print(type(notifications[el]))
            if notifications[el] and type(notifications[el]) is dict and notifications[el]["uid"]:
                print(notifications[el]["uid"])
                users = dict(db.reference("/bot").get())
                for user in users:
                    if user == 'notification':
                        continue
                    if users[user] == notifications[el]["uid"]:
                        action_markup = types.InlineKeyboardMarkup()
                        btn_action = types.InlineKeyboardButton(text='Перейти к уведомлению', url=notifications[el]["link"])
                        action_markup.add(btn_action)
                        bot.send_message(user, notifications[el]["message"], reply_markup=action_markup)
                        # db.reference("/bot/notification/" + str(el)).delete()
            #else:
                # db.reference("/bot/notification/"+str(el)).delete()


bot = telebot.TeleBot("5369765080:AAEb7ZIYF8vS8WgUrSUFLlyC5tMmusdoBQ8")
cred = credentials.Certificate("./firebase-adminsdk.json")
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://runtime-squirrel-default-rtdb.europe-west1.firebasedatabase.app/',
    'storageBucket': 'gs://runtime-squirrel.appspot.com'
})
db.reference("/bot/notification").listen(newNotifications)


def check_auth(tg_id):
    return db.reference("/bot/"+str(tg_id)).get()


def main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Мои проекты')
    itembtn2 = types.KeyboardButton('Информация о пользователе')
    itembtn3 = types.KeyboardButton('Отключить уведомления')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.from_user.id, "Меню:", reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    sent = bot.send_message(message.chat.id, "Привет! Укажите свой идентификатор и получайте уведомления и удобный доступ к информации по проектам.")
    bot.register_next_step_handler(sent, setUID, message.from_user.id)


def setUID(message, uid):
    uid_new = message.from_user.id
    if uid == uid_new:
        db.reference("/bot/"+str(message.from_user.id)).set(message.text)
        bot.send_message(message.from_user.id, "Отлично! Бот подключен к аккуанту " + str(message.text))
        main_menu(message)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    uid = check_auth(message.from_user.id)
    project_markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Назад')
    project_markup.add(itembtn1)
    if uid != "None":
        if message.text == "Мои проекты":
            prdata = db.reference("/projects").get()
            chdata = db.reference("/checkpoints").get()
            print(prdata)
            if prdata:
                for el in prdata:
                    action_markup = types.InlineKeyboardMarkup()
                    btn_action = types.InlineKeyboardButton(text='Перейти к проекту', url="https://quban.tech")
                    action_markup.add(btn_action)
                    if el['status'] == 'current' or el['status'] =='pending':
                        bot.send_message(message.from_user.id, "Название: "+el['title'] + "\nСтатус: в работе")
                        newstr = "empty"
                        for el2 in el['checkpoints']:
                            if chdata[int(el2)]['status'] == 'current' or chdata[int(el2)]['status'] =='pending':
                                if newstr == "empty": newstr = "Текущие контрольной точки:\n\n"
                                dt = random.randint(1, 29)
                                if (dt<10): newstr+="[Скоро дедлайн!]\n"
                                newstr += "Тема контрольной точки: "+chdata[int(el2)]['title'] + "\nВремя дедлайна: "+ str(pd.to_datetime(str(dt)+'-05-2022', infer_datetime_format=True) ) + "\nСтатус: в работе" + "\n\n"
                        if newstr == "Текущие контрольные точки:\n":
                            newstr+= "На данный момент активных задач нет."
                        if newstr != "empty":
                            bot.send_message(message.from_user.id, newstr, reply_markup=action_markup)
                bot.send_message(message.from_user.id, "Что делаем дальше?", reply_markup=project_markup)
        elif message.text == "Информация о пользователе":
            userdata = db.reference("/users/" + str(uid)).get()
            bot.send_message(message.from_user.id, "Nickname: " + userdata["nickname"] + "\nИмя: " + userdata["firstname"] + "\nФамилия: " + userdata["lastname"] + "\nПочта: " + userdata["email"])

        elif message.text == "Информация о пользователеd":
            bot.send_message(message.from_user.id, "sas")
        else:
            main_menu(message)
    else:
        bot.send_message(message.from_user.id, "Вы не авторизованы! Напишите /start и укажите свой уникальный идентификатор.")


bot.infinity_polling()
