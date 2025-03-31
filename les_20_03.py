import random
import requests
import telebot
import json
import os
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_KEY")
MY_DOMAIN = os.getenv("MY_DOMAIN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask(__name__)

quiz_state = {}

def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=uk'
    response = requests.get(url).json()

    if response.get('cod') != 200:
        return "Місто не знайдено. Спробуйте ще раз"
    temp = response['main']['temp']
    desc = response['weather'][0]['description']

    return f'Погода у {city}: Температура: {temp}°C, {desc.capitalize()}'


def get_prediction():
    with open("predictions.txt", "r", encoding="utf-8") as file:
        predictions = file.readlines()
    return random.choice(predictions).strip()


def get_news():
    with open("news.txt", "r", encoding="utf-8") as file:
        news = file.readlines()
    return random.choice(news).strip()


def get_calculator():
    return "Напишіть математичний вираз, наприклад: 2 + 2, 5 * 5, 10 / 2."


def calculate(expression):
    try:
        result = eval(expression)
        return f"Результат: {result}"
    except Exception as e:
        return f"Помилка: {e}"


def get_mood_advice():
    return ("Напишіть ваш настрій (щасливий, сумний, збуджений, розслаблений, злий, лінивий, сонний)")

moods = {
    "щасливий": "Прекрасно! Використовуй цей настрій, щоб досягати нових висот!",
    "сумний": "Не хвилюйся, все буде добре! Візьми час для себе, і настрій покращиться.",
    "збуджений": "Використовуй енергію! Зараз саме час діяти та досягати цілей!",
    "розслаблений": "Чудово! Продовжуй розслаблятись, відпочивай і відновлюй сили.",
    "злий": "Візьми паузу, зроби глибокий вдих і спробуй знайти спокій. Агресія не принесе результатів.",
    "лінивий": "Не турбуйся, але спробуй зробити перший крок. Маленькі завдання допоможуть подолати лінь.",
    "сонний": "Потрібен хороший відпочинок! Якщо можливо, трохи поспи або просто розслабся."
}


def get_quote():
    with open("quotes.txt", "r", encoding="utf-8") as file:
        quotes = file.readlines()
    return random.choice(quotes).strip()


def quiz_question():
    questions = [
        {"question": "Яка столиця України?", "answer": "Київ"},
        {"question": "Хто винайшов телефон?", "answer": "Олександр Белл"},
        {"question": "Яка найбільша планета в Сонячній системі?", "answer": "Юпітер"},
        {"question": "Скільки континентів на Землі?", "answer": "7"},
        {"question": "Хто був першим президентом США?", "answer": "Джордж Вашингтон"},
        {"question": "Скільки кольорів у веселці?", "answer": "7"},
        {"question": "Яка найвища гора в світі?", "answer": "Еверест"},
        {"question": "Яка річка є найдовшою в світі?", "answer": "Амазонка"},
        {"question": "Коли відбулося перше висадження людини на Місяць?", "answer": "1969"},
        {"question": "Який хімічний елемент має символ 'O'?", "answer": "Оксиген"},
        {"question": "Хто написав роман 'Мобі Дік'?", "answer": "Герман Мелвілл"},
        {"question": "Скільки років існує Земля?", "answer": "близько 4.5 мільярдів років"},
        {"question": "Яке місто є столицею Франції?", "answer": "Париж"},
        {"question": "Яка тварина є найбільшим сухопутним ссавцем?", "answer": "Слон"},
        {"question": "Який день тижня йде після понеділка?", "answer": "Вівторок"},
        {"question": "Хто створив теорію відносності?", "answer": "Альберт Ейнштейн"}
    ]
    question = random.choice(questions)
    return question["question"], question["answer"]


user_state = {}
def add_task(message):
    task = message.text.strip()
    chat_id = message.chat.id

    if task:
        try:
            with open("tasks.txt", "a", encoding="utf-8") as file:
                file.write(task + "\n")
            bot.send_message(chat_id, f"Завдання '{task}' додано до списку!")
        except Exception as e:
            bot.send_message(chat_id, f"Сталася помилка при додаванні завдання: {e}")
    else:
        bot.send_message(chat_id, "Ви не вказали завдання. Спробуйте ще раз.")
    del user_state[chat_id]


def get_tasks_list(message):
    try:
        with open("tasks.txt", "r", encoding="utf-8") as file:
            tasks = file.readlines()
            if tasks:
                bot.send_message(message.chat.id,
                                 f"Ваші завдання:\n" + "".join([task.strip() + "\n" for task in tasks]))
            else:
                bot.send_message(message.chat.id, "У вас немає завдань.")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Список завдань порожній або файл не знайдений.")


def show_menu(message):
    menu_text = (
        "Ось всі доступні функції мого бота:\n\n"
        "/start - Привітання з ботом\n"
        "/weather - Погода\n"
        "/prediction - Ваше передбачення на сьогодні\n"
        "/news - Останні новини\n"
        "/calc - Калькулятор\n"
        "/mood - Поради для вас в залежності від вашого настрою\n"
        "/quote - Мотивуюча цитата саме для вас\n"
        "/tasks - Додати завдання до списку справ\n"
        "/tasks_list - Переглянути список справ\n"
        "/del_task - Видалити завдання зі списку справ\n"
        "/quiz - Коротка вікторина\n"

    )
    bot.send_message(message.chat.id, menu_text)


# Обробка повідомлень бота
@bot.message_handler(func=lambda message: True)
def get_message(message):
    chat_id = message.chat.id

    if message.text == "/quiz":
        question, answer = quiz_question()
        quiz_state[chat_id] = {'question': question, 'answer': answer}
        bot.send_message(chat_id, question)
        return

    if chat_id in quiz_state:
        correct_answer = quiz_state[chat_id]['answer']
        user_answer = message.text.strip().lower()

        if user_answer == correct_answer.lower():
            bot.send_message(chat_id, "Чудово! Це правильна відповідь!")
        else:
            bot.send_message(chat_id, f"На жаль, ви не вгадали. Правильна відповідь: {correct_answer}")

        del quiz_state[chat_id]
        return

    if message.text == "/start":
        bot.send_message(chat_id, "Привіт! Напишіть команду /menu щоб побачити які команди я маю.")

    elif message.text == "/prediction":
        bot.send_message(chat_id, get_prediction())

    elif message.text == "/weather":
        bot.send_message(chat_id, "Напишіть назву міста для отримання погоди.")

    elif message.text == "/news":
        bot.send_message(chat_id, get_news())

    elif message.text == "/calc":
        bot.send_message(chat_id, get_calculator())
    elif " " in message.text and (
            message.text.count("+") or message.text.count("-") or message.text.count("*") or message.text.count("/")):
        result = calculate(message.text)
        bot.send_message(chat_id, result)

    elif message.text == "/mood":
        bot.send_message(chat_id, get_mood_advice())
    elif message.text.lower() in moods:
        mood = message.text.lower()
        bot.send_message(chat_id, moods[mood])

    elif message.text == "/quote":
        bot.send_message(chat_id, get_quote())


    elif message.text == "/tasks":
        bot.send_message(chat_id, "Що саме потрібно додати до списку завдань?")
        user_state[chat_id] = "waiting_for_task"

    elif message.text == "/tasks_list":
        get_tasks_list(message)

    elif message.text == "/del_task":
        bot.send_message(chat_id, "Уууу. Ви вже зовсім розлінились! Це ви можете зробити і самі. Просто знайдіть файл tasks, відкрийте його, видаліть певне завдання і збережіть зміни.")

    elif chat_id in user_state and user_state[chat_id] == "waiting_for_task":
        add_task(message)
    elif message.text == "/menu":
        show_menu(message)
        return
    else:
        bot.send_message(message.chat.id, get_weather(message.text))


# Налаштування Webhook
def set_webhook():
    webhook_url = f"{MY_DOMAIN}/{TELEGRAM_TOKEN}"  # Замініть на вашу URL адресу
    bot.set_webhook(url=webhook_url)


@app.route('/')
def index():
    return "Flask сервер працює!"


@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])  # Обробляємо нові оновлення, передані через webhook
    return "OK", 200  # Повертаємо успішну відповідь


if __name__ == "__main__":
    set_webhook()  # Налаштування вебхука
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Використовуйте PORT для Render.com
