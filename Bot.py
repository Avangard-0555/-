import telebot
import buttons as bt
import database as db
from geopy import Photon

geolocator = Photon(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
bot = telebot.TeleBot(token="7639143796:AAE1LPtVUdc4H0VkUhjOoktm4_p9RW3wJKI")
users = {}

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Добро пожаловать в бот доставки!")
    checker = db.check_user(user_id)
    if checker:
        bot.send_message(user_id, "Главное меню: ", reply_markup=bt.main_menu_kb())
    else:
        bot.send_message(user_id, "Введите своё имя для регистрации")
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, "Теперь поделитесь своим номером", reply_markup=bt.phone_button())
    bot.register_next_step_handler(message, get_phone_number, name)

def get_phone_number(message, name):
    user_id = message.from_user.id
    if message.contact:
        phone_number = message.contact.phone_number
        bot.send_message(user_id, "Отправьте свою локацию", reply_markup=bt.location_button())
        bot.register_next_step_handler(message, get_location, name, phone_number)
    else:
        bot.send_message(user_id, "Отправьте свой номер через кнопку в меню")
        bot.register_next_step_handler(message, get_phone_number, name)

def get_location(message, name, phone_number):
    user_id = message.from_user.id
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        address = geolocator.reverse((latitude, longitude)).address

        db.add_user(name=name, phone_number=phone_number, user_id=user_id)
        bot.send_message(user_id, f"Вы успешно зарегистрировались! Ваш адрес: {address}")
        bot.send_message(user_id, "Главное меню: ", reply_markup=bt.main_menu_kb())
    else:
        bot.send_message(user_id, "Отправьте свою локацию через кнопку в меню")
        bot.register_next_step_handler(message, get_location, name, phone_number)

@bot.message_handler(content_types=["text"])
def main_menu(message):
    user_id = message.from_user.id
    if message.text == "🍴Меню":
        all_products = db.get_pr_id_name()
        if not all_products:
            bot.send_message(user_id, "Продукты отсутствуют.")
        else:
            bot.send_message(user_id, "Выберите продукт:", reply_markup=bt.products_in(all_products))
    elif message.text == "🛒Корзина":
        show_cart(user_id)
    elif message.text == "✒️Отзыв":
        bot.send_message(user_id, "Напишите текст вашего отзыва:")
        bot.register_next_step_handler(message, handle_feedback)

def show_cart(user_id):
    cart = db.get_user_cart(user_id)
    full_text = "Ваша корзина:\n"
    total_price = 0
    for idx, product in enumerate(cart, 1):
        full_text += f"{idx}. {product[0]} x {product[1]} = {product[2]}\n"
        total_price += product[2]
    bot.send_message(user_id, full_text + f"\nИтоговая сумма: {total_price} сум",
                     reply_markup=bt.get_cart_kb(db.get_card_id_name(user_id)))

def handle_feedback(message):
    user_id = message.from_user.id
    feedback = message.text
    # Логика сохранения или отправки отзыва
    bot.send_message(user_id, "Спасибо за ваш отзыв!")

@bot.callback_query_handler(lambda call: call.data == "order")
def order(call):
    user_id = call.message.chat.id
    cart = db.get_user_cart(user_id)
    user_info = db.get_all_users()
    user_data = [u for u in user_info if u[0] == user_id][0]  # Получаем имя и номер клиента
    name, phone_number = user_data[1], user_data[2]

    full_text = f"Новый заказ от {name} (тел: {phone_number}):\n"
    total_price = 0
    for idx, product in enumerate(cart, 1):
        full_text += f"{idx}. {product[0]} x {product[1]} = {product[2]}\n"
        total_price += product[2]

    # Отправляем информацию менеджеру
    manager_chat_id = -4547664725
    bot.send_message(manager_chat_id, full_text + f"\nИтоговая сумма: {total_price} сум")

    # Добавляем кнопки "Принят" и "Отклонен"
    markup = telebot.types.InlineKeyboardMarkup()
    accepted = telebot.types.InlineKeyboardButton("Принят", callback_data="accepted")
    declined = telebot.types.InlineKeyboardButton("Отклонен", callback_data="declined")
    markup.add(accepted, declined)

    bot.send_message(manager_chat_id, "Статус заказа:", reply_markup=markup)
    bot.send_message(user_id, "Ваш заказ принят и обрабатывается оператором", reply_markup=bt.main_menu_kb())
    db.delete_user_cart(user_id)

@bot.callback_query_handler(lambda call: call.data in ["accepted", "declined"])
def order_status(call):
    if call.data == "accepted":
        bot.send_message(call.message.chat.id, "Заказ принят!")
    elif call.data == "declined":
        bot.send_message(call.message.chat.id, "Заказ отклонен!")

bot.infinity_polling()
