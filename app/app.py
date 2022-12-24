from aiogram import Bot, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from random import randrange
from requests.adapters import HTTPAdapter
import time
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


TOKEN = 'INSERT YOUR TOKEN HERE'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


types = {'Общий': '', 'Любовный': 'love-', 'Финансовый': 'finance-', 'Здоровья': 'health-'}
signs = {'овен': 'aries', 'телец': 'taurus', 'близнецы': 'gemini', 'рак': 'cancer', 'лев': 'leo', 'дева': 'virgo',
         'весы': 'libra', 'скорпион': 'scorpio', 'стрелец': 'sagittarius',
         'козерог': 'capricorn', 'водолей': 'aquarius', 'рыбы': 'pisces'}
dates = {'На сегодня': '', 'На завтра': 'tomorrow', 'На неделю': 'week'}
genders = ['Не важно', 'Мужчина', 'Женщина']

marks = ['червей', 'бубен', 'пик', 'треф']
emojis = ['♥', '♦', '♠', '♣']
values = ["Шестерка", "Семерка", "Восьмерка", "Девятка", "Десятка", "Валет", "Дама", "Король", "Туз"]
tr_marks = ['chervej', 'buben', 'pik', 'tref']
tr_values = ['shesterka', 'semerka', 'vosmerka', 'devyatka', 'desyatka', 'valet', 'dama', 'korol', 'tuz']

answers = [['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да', 'Можешь быть уверен в этом'],
           ['Мне кажется — «да»', 'Вероятнее всего', 'Хорошие перспективы', 'Знаки говорят — «да»', 'Да'],
           ['Пока не ясно, попробуй снова', 'Спроси позже', 'Лучше не рассказывать', 'Сейчас нельзя предсказать',
            'Сконцентрируйся и спроси опять'],
           ['Даже не думай', 'Нет', 'По моим данным — «нет»', 'Перспективы не очень хорошие', 'Весьма сомнительно']]


class Horoscope(StatesGroup):
    type = State()
    sign = State()
    date = State()
    gender = State()


@dp.message_handler(commands=['start'], state="*")
async def start(message, flag=True):
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    hor = KeyboardButton('Гороскоп')
    pred = KeyboardButton('Шар с предсказаниями')
    card = KeyboardButton('Совет от карт ')
    buttons.add(hor, pred, card)
    if flag:
        await message.answer("Привет! Я бот для предсказаний! Выбери одну из доступных опций🪬", reply_markup=buttons)
    else:
        await message.answer("Снова ты! Выбери одну из доступных опций🪬", reply_markup=buttons)


@dp.message_handler(lambda message: message.text == "Гороскоп", state='*')
async def horoscope(message):
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    base = KeyboardButton('Общий')
    love = KeyboardButton('Любовный')
    money = KeyboardButton('Финансовый')
    health = KeyboardButton('Здоровья')
    buttons.add(base, love, money, health)
    await message.answer("Cкорее приступим! Выбери вид гороскопа🪐 ", reply_markup=buttons)
    await Horoscope.type.set()


@dp.message_handler(state=Horoscope.type)
async def get_type(message, state):
    text = message.text
    if text not in types:
        await message.answer('Выбери вид из предложенных!')
        return
    async with state.proxy() as data:
        data['type'] = types[text]
    buttons = ReplyKeyboardRemove()
    await Horoscope.sign.set()
    await message.answer('Введи свой знак зодиака 🌀', reply_markup=buttons)


@dp.message_handler(state=Horoscope.sign)
async def get_sign(message, state):
    text = message.text.lower()
    if text not in signs:
        await message.answer('Введи корректный знак зодиака!')
        return
    async with state.proxy() as data:
        data['sign'] = signs[text]
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    today = KeyboardButton('На сегодня')
    tomorrow = KeyboardButton('На завтра')
    week = KeyboardButton('На неделю')
    buttons.add(today, tomorrow, week)
    await Horoscope.date.set()
    await message.answer('Здорово! Теперь выбери период для гороскопа 🕐', reply_markup=buttons)


@dp.message_handler(state=Horoscope.date)
async def get_date(message, state):
    text = message.text
    if text not in dates:
        await message.answer('Что-то пошло не так, выбери период из предложенных')
        return
    async with state.proxy() as data:
        data['date'] = dates[text]
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    male = KeyboardButton('Мужчина')
    female = KeyboardButton('Женщина')
    dont = KeyboardButton('Не важно')
    buttons.add(male, female, dont)
    await Horoscope.gender.set()
    await message.answer('Теперь укажи гендер 👤', reply_markup=buttons)


@dp.message_handler(state=Horoscope.gender)
async def get_gender(message, state):
    text = message.text
    if text not in genders:
        await message.answer('Что-то пошло не так, укажи гендер из предложенных')
        return
    async with state.proxy() as data:
        type = data['type']
        sign = data['sign']
        period = data['date']
    await state.finish()

    await message.answer('Терпения, мой друг! Связываюсь со звездами и жду ответа!')

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    url = 'https://astrohelper.ru/' + type + 'horoscope/' + sign + '/' + period
    r = session.get(url)

    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    horoscope = []
    for div in soup.find_all('div', {'class': "mt-3"}):
        for x in div.find_all('p'):
            horoscope.append(x.get_text())
    buttons = ReplyKeyboardMarkup(resize_keyboard=True)
    again = KeyboardButton('Заново')
    buttons.add(again)
    periods = {'': 'на сегодня', 'tomorrow': 'на завтра', 'week': 'на неделю'}

    text_message = 'Вот твой '
    if type == 'love-':
        text_message += 'любовный '
    if type == 'finance-':
        text_message += 'финансовый '
    text_message += 'гороскоп '
    if type == 'health-':
        text_message += 'здоровья '
    text_message += periods[period] + '🌟\n\n'
    await message.answer(text_message + horoscope[genders.index(text)], reply_markup=buttons)


@dp.message_handler(lambda message: message.text == 'Совет от карт', state='*')
async def card(message):
    buttons = InlineKeyboardMarkup()
    card = InlineKeyboardButton('🃏', callback_data="card")
    buttons.add(card)
    await message.answer(
        "Вытащите свою карту из колоды игральных карт — она расскажет, что вас ждёт, поможет стать лучше и рассеет сомнения в предстоящем дне.",
        reply_markup=buttons)


@dp.callback_query_handler(text="card")
async def get_card(call):
    await call.message.answer('Судьба выбирает карту...')
    mark = randrange(4)
    value = randrange(9)
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    url = 'https://gadalkindom.ru/gadanie/karty-igralnye/' + tr_values[value] + '_' + tr_marks[mark] + '.html'
    r = session.get(url)
    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')
    for article in soup.find_all('section', {'itemprop': "articleBody"}):
        if mark > 0:
            x = article.find_all('p')
            text = x[11].get_text()
        else:
            x = article.find_all('ul')
            x = x[2].find_all('li')
            text = x[2].get_text()[13:]
    if text == '':
        text = 'Время остановиться и посмотреть вокруг. Возможно, скоро придёт час, когда нужно будет собирать камни, а ' \
               'не разбрасывать их. Поможет выстоять в этот не самый простой период очень близкий для вас человек – не только словом, но и делом.'
    choice = f'Ваша карта: {values[value]} {marks[mark]} {emojis[mark]}\n\nСовет карты: '
    await call.message.answer(choice + text)


@dp.message_handler(lambda message: message.text == 'Шар с предсказаниями', state='*')
async def pred(message):
    buttons = InlineKeyboardMarkup()
    card = InlineKeyboardButton('🔮', callback_data="pred")
    buttons.add(card)
    await message.answer(
        "Внимательно сосредоточься на интересующем тебя вопросе, произнеси его вслух и нажми на шар!",
        reply_markup=buttons)


@dp.callback_query_handler(text="pred")
async def get_pred(call):
    await call.message.answer('Магический шар думает...')
    time.sleep(3)
    await call.message.answer(answers[randrange(4)][randrange(5)])


@dp.message_handler(lambda message: message.text == "Заново", state='*')
async def again(message):
    await start(message, False)


if __name__ == '__main__':
    executor.start_polling(dp)
