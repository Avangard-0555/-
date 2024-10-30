import telebot

bot = telebot.TeleBot(token="7639143796:AAE1LPtVUdc4H0VkUhjOoktm4_p9RW3wJKI")

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.username
    bot.send_message(user_id, f"Добро пожаловать {name} ")
    bot.send_message(user_id, "Введите свой имя для регистрации")
    bot.register_next_step_handler(message, get_name1)
def get_name1(message):
    user_id = message.from_user.id
    #Обращается по нику
    name1 = message.text
    bot.send_message(user_id, "Теперь поделитесь своим номером")
#Перешагивает на следуюший этап
    bot.register_next_step_handler(message,phone_number)
def phone_number(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Отправьте свою локацию")
    bot.register_next_step_handler(message, location)

def location(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Отправьте свою локацию")
    bot.register_next_step_handler(message, phone_number)


bot.infinity_polling()
