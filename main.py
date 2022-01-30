import json
import telebot
import requests as req
from geopy import geocoders
from os import environ

token = environ['5165695941:AAH_-sdbx8r0i8J4WEVonuMnoxoOR6Fzz-0']
token_openw = environ['90b61d79308e1b5d0424a2d187eb1c2c']

bot = telebot.TeleBot(token)

with open('citi es.json', encoding='utf-8') as f:
    cities = json.load(f)
#іввфв
bot.polling(none_stop=True)

def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude

def code_location(latitude: str, longitude: str, token_openw: str):
    url_location_key = f'pro.openweathermap.org/data/2.5/forecast/hourly?lat={latitude}&lon={longitude}&appid={"APIKey": token_openw}'
    resp_loc = req.get(url_location_key, headers={"APIKey": token_openw})
    json_data = json.loads(resp_loc.text)
    code = json_data['Key']
    return code

def weather(code_loc: str, token_openw: str):
    url_weather = f'pro.openweathermap.org/data/2.5/forecast/hourly?id={code_loc}&appid={"APIkey": token_openw}'
    response = req.get(url_weather, headers={"APIKey": token_openw})
    json_data = json.loads(response.text)
    dict_weather = dict()
    dict_weather['link'] = json_data[0]['list']['main']
    dict_weather['now'] = {'temp': json_data[0]['list']['main']['temp'], 'pressure': json_data[0]['list']['main']['pressure'], 'clouds': json_data[0]['list']['clouds']['all']}
    for i in range(1,len(json_data)):
        time = 'через' + str(i) + 'ч'
        dict_weather[time] = {'temp': json_data[i]['list']['main']['temp'], 'pressure': json_data[i]['list']['main']['pressure'], 'clouds': json_data[i]['list']['clouds']['all']}
    return dict_weather

def print_weather(dict_weather, message):
    bot.send_message(message.from_user.id, f'Оперативная справка:'
                                           f' Температура сейчас {dict_weather["now"]["temp"]}'
                                           f' А небо затянуто облаками на {dict_weather["now"]["clouds"]}% '
                                           f' Температура через три часа {dict_weather["через3ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через3ч"]["clouds"]}%.'
                                           f' Температура через шесть часов {dict_weather["через6ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через6ч"]["clouds"]}%.'
                                           f' Температура через девять часов {dict_weather["через9ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через9ч"]["clouds"]}.')
    bot.send_message(message.from_user.id, f' А здесь ссылка на подробности'
                                           f'{dict_weather["link"]}')

def big_weather(message, city):
    latitude, longitude = geo_pos(city)
    cod_loc = code_location(latitude, longitude, token_openw)
    you_weather = weather(cod_loc, token_openw)
    print_weather(you_weather, message)

def add_city(message):
    try:
        latitude, longitude = geo_pos(message.text.lower().split('город ')[1])
        global cities
        cities[message.from_user.id] = message.text.lower().split('город ')[1]
        with open('cities.json', 'w') as f:
            f.write(json.dumps(cities))
        return cities, 0
    except Exception as err:
        return cities, 1

@bot.message_handler(command=['start', 'help'])
def send_welcome(message):
    bot.send_photo(message, photo='postimg.cc/njbDqqsW', caption=f' Привет! Я ботолег! Будем знакомы, {message.from_user.first_name}.')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global cities
    if message.text.lower() == 'привет' or message.text.lower() == 'здорова':
        bot.send_message(message.from_user.id,
                         f'Многоуважаемый {message.from_user.first_name}! Давайте Я расскажу '
                         f' Вам о погоде! Напишите  слово "погода" и я напишу погоду в Вашем'
                         f' городе "по умолчанию" или напишите название города в котором Вы сейчас')
    elif message.text.lower() == 'погода':
        if message.from_user.id in cities.keys():
            city = cities[message.from_user.id]
            bot.send_message(message.from_user.id, f'Pozdravlyayudalbaeb {message.from_user.first_name}!'
                                                   f' Твой город {city}')
            big_weather(message, city)

        else:
            bot.send_message(message.from_user.id, f'Уважаемый {message.from_user.first_name}!'
                                                   f' Я не знаю Ваш город! Просто напиши:'
                                                   f'"Мой город *****" и я запомню твой стандартный город!')
    elif message.text.lower()[:9] == 'мой город':
        cities, flag = add_city(message)
        if flag == 0:
            bot.send_message(message.from_user.id, f'Molodecschusenek {message.from_user.first_name}!'
                                                   f' Теперь я знаю Ваш город! это'
                                                   f' {cities[str(message.from_user.id)]}')
        else:
            bot.send_message(message.from_user.id, f'Sorryschusenek {message.from_user.first_name}!'
                                                   f' Что то пошло не так :(')
    else:
        try:
            city = message.text
            bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}! Твой город {city}')
            big_weather(message, city)
        except AttributeError as err:
            bot.send_message(message.from_user.id, f'{message.from_user.first_name}! Ты шо шутки'
                                                   f' шутишь?  Я не нашел такого города! Наебсик!'
                                                   f'И получил ошибку {err}, попробуй другой город')