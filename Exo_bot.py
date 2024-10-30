#перед началом в терминале пишем pip install telebot
import telebot
from telebot.util import user_link

token = "7639143796:AAE1LPtVUdc4H0VkUhjOoktm4_p9RW3wJKI"
#создаем обьект бота
bot = telebot.TeleBot(token=token)
@bot.message_handler(commands=["start","help"])
def start(message):
    #кому бот обращается
    user_id = message.from_user.id
    #тут бот обращается по username
    name = message.from_user.username
    bot.send_message(user_id, f"HI {name}")
@bot.message_handler(content_types=["text"])
def text (message):
    user_id = message.from_user.id
    user_text = message.text
    bot.send_message(user_id, user_text)




#Создаем команду для бесконечной работы бота
bot.infinity_polling()
#второй вариант
#bot.polling(non_stop=True)
