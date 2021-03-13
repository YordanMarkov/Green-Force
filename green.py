#!/usr/bin/env python

import falcon
from wsgiref import simple_server
import os
import sys
import json
import random
import requests

cities = {
    'paris': {
        'weather': 2968815,
        'waqi': 'paris'
    },
    'london': {
        'weather': 7535661,
        'waqi': 'london'
    },
    'rio_de_janeiro': {
        'weather': 3469034,
        'waqi': 'brazil'
    },
    'sofia': {
        'weather': 727011,
        'waqi': 'sofia'
    },
    'new_york': {
        'weather': 5128594,
        'waqi': 'newyork'
    },
    'sydney': {
        'weather': 2147714,
        'waqi': 'sydney'
    },
    'tokyo': {
        'weather': 1850144,
        'waqi': 'tokyo'
    },
    'moscow': {
        'weather': 6198441,
        'waqi': 'moscow'
    },
    'hong_kong': {
        'weather': 1819729,
        'waqi': 'hongkong'
    },
}


def get_weather(city='sofia'):
    APIKEY = 'be33ea2b313dc9a0720ba44df2ac8d5e'
    id = cities[city]['weather']
    print('http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}'.format(id, APIKEY))
    data = requests.get('http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}'.format(id, APIKEY))
    data.raise_for_status()
    return data.json()


def wagi_data(city='sofia'):
    TOKEN = 'f6160ea3cb21c32e1e136b2f306fabbb44980b15'
    id = cities[city]['waqi']
    print('https://api.waqi.info/feed/{}/?token={}'.format(id, TOKEN))
    data = requests.get('https://api.waqi.info/feed/{}/?token={}'.format(id, TOKEN))
    data.raise_for_status()
    return data.json()


class DataResource(object):
    def on_get(self, req, resp):
        city = 'sofia'
        if 'city' in req.params:
            city = req.params['city']
        print(city)
        weather = get_weather(city)
        print(weather)
        wagi = wagi_data(city)
        print(wagi)
        try:
            aqi = int(wagi['data']['aqi'])
        except:
            aqi = 0
        data = {
            'temp': weather['main']['temp'],
            'temp_min': weather['main']['temp_min'],
            'temp_max': weather['main']['temp_max'],
            'img': 'http://openweathermap.org/img/wn/{}@4x.png'.format(weather['weather'][0]['icon']),
            'pre': weather['main']['pressure'],
            'hum': weather['main']['humidity'],
            'aqi': aqi,
            'no2': 0,
            'o3': 0,
            'pm10': 0,
            'pm2_5': 0,
            'recommend': '',
            'reasons': '',
            'health': '',
            'background': '/web/background/womple_new_background.png'
        }

        if 'o3' in wagi['data']['iaqi']:
            data['o3'] = wagi['data']['iaqi']['o3']['v']
        if 'pm10' in wagi['data']['iaqi']:
            data['pm10'] = wagi['data']['iaqi']['pm10']['v']
        if 'pm25' in wagi['data']['iaqi']:
            data['pm2_5'] = wagi['data']['iaqi']['pm25']['v']
        if 'no2' in wagi['data']['iaqi']:
            data['no2'] = wagi['data']['iaqi']['no2']['v']
        if data['o3'] >= 120:
            data['recommend'] += 'Завишено ниво на озон! Излез навън, само ако е наложително!<br>'
            data['reasons'] += 'Озон:<br>Взаимодействието на азотните оксиди и летливите органични съединения под влияние на високи температури и слънчева светлина<br>'
            data['health'] += 'Последици от озона:<br>Възпрепятства доставката на кислород от хемоглобина до тъканите, в по-висока концентрация задушаване, кома или смърт.<br>'
        if data['pm10'] >= 50:
            data['recommend'] += 'Високо ниво на прахови частици PM10:<br>Сложете маска с филтър, ако излизате навън!<br>'
            data['reasons'] += 'PM10:<br>Стопанска дейност, транспорт, отопление, селско стопанство, строителство, офис оборудване<br>'
            data['health'] += 'Последици от PM10:<br>Засилването на алергиите, асматични пристъпи, дихателни смущения, рак на белия дроб<br>'
        if data['pm2_5'] >= 25:
            data['recommend'] += 'Високо ниво на прахови частици PM2.5:<br>Сложете маска с филтър, ако излизате навън!<br>'
            data['reasons'] += 'PM2.5:<br>Стопанска дейност, транспорт, отопление, селско стопанство, строителство, офис оборудване<br>'
            data['health'] += 'Последици от PM2.5:<br>Засилването на алергиите, асматични пристъпи, дихателни смущения, рак на белия дроб<br>'
        if data['no2'] >= 200:
            data['recommend'] += 'Високо ниво на Азотен диоксид (NO2):<br>Не използвай кола, качи се на градския транспорт! Не стой в близост до тютюнопушачи!<br>'
            data['reasons'] += 'Азотен диоксид (NO2):<br>Моторните превозни средства (МПС), топлоелектрическите централи (ТЕЦ), някои промишлени предприятия, тютюнопушенето<br>'
            data['health'] += 'Последици от азотен диоксид (NO2):<br>Структурни промени в белия дроб<br>'
        if data['aqi'] > 0 and data['aqi'] <= 50:
            data['recommend'] += 'Въздушният индекс показва:<br>Няма опасност за здравето ти!<br>'
        if data['aqi'] > 50 and data['aqi'] <= 100:
            data['recommend'] += 'Въздушният индекс показва:<br>Въздухът е сравнително чист, но все пак има малка опасност!<br>'
        if data['aqi'] > 100 and data['aqi'] <= 150:
            data['recommend'] += 'Въздушният индекс показва:<br>Ако имаш заболявания, стой си вкъщи!<br>'
        if data['aqi'] > 150 and data['aqi'] <= 200:
            data['recommend'] += 'Въздушният индекс показва:<br>Излез навън, само ако е наложително!<br>'
        if data['aqi'] > 200 and data['aqi'] <= 300:
            data['recommend'] += 'Въздушният индекс показва:<br>Сложете маска с филтър, ако излизате навън и то само ако е наложително!<br>'
        if data['aqi'] > 300 and data['aqi'] <= 500:
            data['recommend'] += 'Въздушният индекс показва:<br>Стой вкъщи задължително!<br>'
        if os.path.exists('web/background/womple_{}.png'.format(city)):
            data['background'] = '/web/background/womple_{}.png'.format(city)
        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_200


class PhotoResource(object):
    def on_get(self, req, resp):
        mypath="web/actions"
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        data = {
            'photo': '/web/actions/' + onlyfiles[random.randint(0, len(onlyfiles)-1)]
        }
        resp.body = json.dumps(data)
        resp.status = falcon.HTTP_200


class HtmlAdapter(object):
    def __call__(self, req, resp):
        file_full_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        file_name = "{}{}".format(file_full_path, req.relative_uri)
        if os.path.exists(file_name) and os.path.isfile(file_name):
            resp.body = open(file_name, 'rb').read()
            ext = file_name.split(".")[-1]
            if ext == 'html':
                resp.content_type = 'text/html'
            elif ext in ['png', 'jpg']:
                resp.content_type = 'image/' + ext
            elif ext == 'js':
                resp.content_type = 'application/javascript'
            elif ext == 'css':
                resp.content_type = 'text/css'
            else:
                resp.content_type = 'text/plain'
        elif req.relative_uri.find('/web') == 0:
            resp.body = open("{}/web/index.html".format(file_full_path)).read().encode('cp1251')
            resp.content_type = 'text/html'
        else:
            resp.body = 'Not found!'
            resp.content_type = 'text/html'
            resp.status = falcon.HTTP_404
            return
        resp.status = falcon.HTTP_200


api = falcon.API()
api.add_route('/data', DataResource())
api.add_route('/photo', PhotoResource())
api.add_sink(HtmlAdapter(), '/web')

if __name__ == '__main__':
    ip = "0.0.0.0"
    port = 6868
    print("Start server at {}:{}".format(ip, port))
    httpd = simple_server.make_server(ip, port, api)
    httpd.serve_forever()
