import telebot
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

bot = telebot.TeleBot("5369765080:AAEb7ZIYF8vS8WgUrSUFLlyC5tMmusdoBQ8")
cred = credentials.Certificate("./firebase-adminsdk.json")

default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://runtime-squirrel-default-rtdb.europe-west1.firebasedatabase.app/',
    'storageBucket': 'gs://runtime-squirrel.appspot.com'
})
users_database = {
    "1": {
        "username": "test",
        "last_activity": 1619212557
    },
    "2": {
        "username": "test",
        "last_activity": 1603212638
    }
}
db.reference("/users_database/").set(users_database)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.infinity_polling()
