#!/usr/bin/python2.7
# -*- coding: utf8 -*-

import glob
import os
import StringIO
import json
import logging
import random
import urllib
import urllib2
import tweepy
import requests

BASE_URL = 'https://api.telegram.org/bot'
Token = '109206957:' #ticker bot VERDE
#TOKEN = '110309400:' #rabit bot

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from flask import request, send_from_directory, jsonify , Flask, url_for , json

application = Flask(__name__)
app = application





auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)


def UltimoTweet():

    for tweets in api.user_timeline('BTCicker',count=1):

        text = tweets.text

    return text

    #r = api.request('statuses/user_timeline', {'screen_name ':'BTCicker' })

    #for item in r.get_iterator():
    #print ">", item
    #    if 'text' in item:
    #        print item['text']
    #print r.__dict__

    #item = r.get_iterator()
    #last_t = next(item)
    #return  last_t['text']

def LanzaConsulta(url):

    hdr = {'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.4; Desire HD Build/KTU84Q)'}
    req = urllib2.Request(url,headers=hdr)
    page = urllib2.urlopen(req)
    data = json.loads(page.read())

    return data

def eltiempo(text):

    ciudad = text.split()
    consulta = ""

    for i in range(1,len(ciudad)):

        consulta = consulta +" "+ ciudad[i]

    ApiKey = ""

    consulta = urllib.quote_plus(consulta.encode('ascii','replace'))



    url="https://apidev.accuweather.com/locations/v1/es/search?q="+consulta+"&apikey="+ApiKey

    data = LanzaConsulta(url)

    CodigoCiudad = '303963'

    if len(data) > 0 :

        CodigoCiudad = unicode(data[0]['Key'])

        ##https://api.accuweather.com/currentconditions/v1/303963?apikey=srRLeAmTroxPinDG8Aus3Ikl6tLGJd94
        url="https://api.accuweather.com/currentconditions/v1/"+CodigoCiudad+"?apikey="+ApiKey+"&details=true&language=es"

        data = LanzaConsulta(url)

        RelativeHumidity = unicode(data[0]['RelativeHumidity'])
        WeatherText = unicode(data[0]['WeatherText'])
        Temperature = unicode(data[0]['Temperature']['Metric']['Value'])
        Pressure = unicode(data[0]['Pressure']['Metric']['Value'])
        WindS = unicode(data[0]['Wind']['Speed']['Metric']['Value'])
        WindD = unicode(data[0]['Wind']['Direction']['Degrees'])
        WindD2 = unicode(data[0]['Wind']['Direction']['Localized'])
        UVIndexText = unicode(data[0]['UVIndexText'])
        PressureTendency = unicode(data[0]['PressureTendency']['LocalizedText'])

        message = WeatherText + "  "+Temperature+ u"ºC"+" Humedad: "+RelativeHumidity+"%  PA: "+Pressure+" mb\n"
        message = message +"Viento: "+WindS+"km/h "+WindD+ u"º"+WindD2+" Indice_UV: " +UVIndexText + u" Presión: "+PressureTendency


        url="https://api.accuweather.com/alerts/v1/303963?apikey=srRLeAmTroxPinDG8Aus3Ikl6tLGJd94&details=true&language=es"

        data = LanzaConsulta (url)

        #logging.debug("..........Data.............")

        #logging.debug(len(data))

        Localized = "";

        if len (data) > 0 :

            Localized = unicode(data[0]['Description']['Localized'])

        msg = message + "\n" + Localized


    else :

        msg = 'Ciudad no encontrada.'


    return msg

def GetTickerData():

    lasteur_btc = ""
    lastusd_btc = ""
    _coindesk = ""
    _btce = ""
    _kraken = ""
    _btchina = ""
    _okcoin = ""
    _bitfix = ""

    url="https://btc-e.com/api/3/ticker/btc_eur"
    data = LanzaConsulta(url)
    if not (data == "") :
        lasteur_btc = unicode(round(data['btc_eur']['last'],2))


    url="https://api.bitfinex.com/v1/pubticker/btcusd"
    data = LanzaConsulta(url)

    #last = unicode(round(data['last_price'],2)) Se les ocurre la genial idea de poner las cantidades como string XD
    last = data['last_price']

    _bitfix = "Bitfinex:  USD "+last +"\n"


    url="https://api.kraken.com/0/public/Ticker?pair=XXBTZEUR"
    #Parece que a la gente de Kraken no les gusta que python carge sus datos , porque con php no me pasaba
    data = LanzaConsulta(url)
    # Formatea una cadena a dos decimales. con Split('.') y luego last = '%s.%s%%' % (la[0], la[1][:2])
    la = data['result']['XXBTZEUR']['c'][0].split('.')
    last = '%s.%s' % (la[0], la[1][:2])
    _kraken = "Kraken: EUR "+ last +"\n"


    url="https://data.btcchina.com/data/ticker?market=btccny"
    data = LanzaConsulta(url)

    last = data['ticker']['last']
    _btchina = "BTC China: CNY "+last +"\n"

    url="https://www.okcoin.com/api/ticker.do?ok=1"
    data = LanzaConsulta(url)

    last = data['ticker']['last']
    _okcoin = "OKCoin:    USD "+ last +"\n"

    url="https://api.coindesk.com/v1/bpi/currentprice.json"
    data = LanzaConsulta(url)

    last_usd = unicode(round(data['bpi']['USD']['rate_float'],2))
    last_eur = unicode(round(data['bpi']['EUR']['rate_float'],2))
    #last_gbp = unicode(round(data->bpi->GBP->rate_float,2))

    _coindesk = "CDesk:  EUR "+ last_eur +" USD "+ last_usd + "\n"

    url="https://btc-e.com/api/3/ticker/btc_usd"

    data = LanzaConsulta(url)
    if not (data == "") :

        lastusd_btc = unicode(round(data['btc_usd']['last'],2))

    _btce = "BTC-e :   EUR "+lasteur_btc +"  USD "+lastusd_btc+"\n"

    message = _coindesk + _btce + _kraken + _btchina + _okcoin + _bitfix

    return message


@app.route('/')
def root():

    return app.send_static_file('index.html')


@app.route('/estrenodtl', methods = ['POST'])

def estrenodtl():

    body = request.get_data()

    #logging.error(body)

    
    msg = body
    
    chat_id = '6660201'
    
    reply(msg,chat_id,Token)

    return  json.dumps(200)




@app.route('/cuadra', methods = ['GET'])

def cuadra():
    
    #logging.error(os.getcwd())

    newest = max(glob.iglob('./huerta/*.jpg'), key=os.path.getctime)
   
    Token = '137388301:AAHWFhSC7XQBBltMLheRMXtf-BiZ_ZH4YS4'

    chat_id = '6660201'
      
    sendimage(newest,chat_id,Token)
    
    chat_id = '14515115' # Lalo
    
    sendimage(newest,chat_id,Token)
    
    return  json.dumps(200)





@app.route('/webhook', methods = ['GET'])

def setwebhook():
    resp = LanzaConsulta(BASE_URL+"setwebhook?url="+"https://tiki.alwaysdata.net/verde")
    
    return json.dumps(resp)



@app.route('/verde', methods = ['POST'])

def webhook():
   
    body = request.get_json()

    logging.error(body)


    
        
    update_id = body['update_id']
    message = body['message']
    message_id = message.get('message_id')
    date = message.get('date')
    
    fr = message.get('from')
    chat = message['chat']
    chat_id = chat['id']

    # Si el mensaje es un fichero .....
        
    if message.get('document'):
        
        document = message.get('document')
        file_id = document['file_id']

           
        msg = file_id

        reply(msg,chat_id)
                
        
    else:
        
    
    # Si el mensaje no es un fichero, entonces debe ser un texto    
        
        
        text = message.get('text')    


        if text.startswith('/t '):

            msg = (eltiempo(text))

            reply(msg,chat_id)



        if text.startswith('/ticker'):

            # Pilla los datos de las API de cada servidor
            #msg = GetTickerData()

            # Pilla el ultimo twit del ticker
            msg = UltimoTweet()

            reply(msg,chat_id)


        if text.startswith('/d'):

            # Pilla los datos de las API de cada servidor
            msg = GetTickerData()

            # Pilla el ultimo twitt del ticker
            # msg = UltimoTweet()

            reply(msg,chat_id)      
    
     
      
    
    return  json.dumps(body)




def reply(msg,chat_id):
    
    url = BASE_URL + Token + '/sendMessage' 

    r = requests.post(url, data = { 
    'chat_id':chat_id ,'text': msg.encode('utf-8'),
    'disable_web_page_preview': 'true' , 'reply_to_message_id': '' 
        })
    return


def sendimage(image,chat_id,Token):

    url = BASE_URL + Token + '/sendPhoto' 
            
   
    files = {'photo': open(image, 'rb')}
    
    r = requests.post(url,files=files, data={ 'photo':image,'chat_id':chat_id })
    
    
    return


if __name__ == '__main__':
   #app.debug = True
    app.run()
