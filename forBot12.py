import requests  
import datetime
import constants
import csv

'''
Telegram-bot @btc4dipp_bot

This robot tells jokes in three languages - pl, en, ru
If you write your own, he will read with pleasure :)

After the greeting, the bot displays the text of the joke in the user's greeting language.

The author of the script and the telegram-bot: 375411664dip@gmail.com, @dipp_free
'''

token = constants.token
my_path = constants.my_path
logfile = constants.logfile

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=300): # timeout
        method = 'getUpdates'
        params = {'timeout' : timeout, 'offset' : offset}
        resp = requests.post(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp



def get_message(last_update): # to get a start, pl, en or ru from the user, and write down his data and text
    try:
        last_chat_text = last_update['message']['text']
        last_chat_lang = last_update['message']['from']['language_code']
    except: 
        last_chat_text = '/start'  # if user sent me no text
        last_chat_lang = 'ru'      # default language

    if last_chat_text.lower() in ('cześć!', 'hello!', 'привет!', 'hi', 'cześć', 'hello', 'привет', '/contacts'):
        last_chat_text = '/start'

    last_update_id = last_update['update_id']
    last_chat_id = last_update['message']['from']['id']
    last_chat_name = last_update['message']['from']['first_name']
    

    now = datetime.datetime.now()
    with open(my_path+logfile, 'a') as m: # logging
        todb = ', '.join([now.strftime("%d/%m/, %H:%M:%S"), 
                last_chat_name, str(last_chat_id), last_chat_lang])
        m.write(todb+'\n'+last_chat_text+'\n\n')


    if last_chat_text.lower() in ('/start', 'pl', 'en', 'ru'):
        send_answer(last_chat_id, last_chat_text.lower(), last_chat_name, last_chat_lang)
    elif len(last_chat_text) > 40:
        send_answer(last_chat_id, 'joke', last_chat_name, last_chat_lang)
    else:
        greet_bot.send_message(last_chat_id, 'This is not a joke, {}.'.format(last_chat_name))



def send_answer(last_chat_id, answ, usname, lang): # response to user

    answr_en = '\n\nWrite me some joke here.\nNo?\nThen write PL, EN or RU, and next one I`ll take from this country'.format(usname)
    answr_ru = '\n\nНапиши мне свой анекдот.\nНет?\nТогда напиши PL, EN или RU, и следующий я возьму из этой страны'.format(usname)
    answr_pl = '\n\nNapisz mi jakiś dowcip.\nNie?\nTo pisz PL, EN lub RU, a następny będzie z tego kraju'.format(usname)

    if answ in ('/start', 'pl', 'en', 'ru'):
        if answ in ('pl', 'en', 'ru'): myjoke = tell_joke(answ, last_chat_id)
        if answ == '/start': myjoke = tell_joke(lang, last_chat_id)
        # exit()

        if lang == 'pl':
            allansw = myjoke+answr_pl
        elif lang == 'ru' or lang == 'ua':
            allansw = myjoke+answr_ru
        else:
            allansw = myjoke+answr_en

        greet_bot.send_message(last_chat_id, allansw)


    if answ == 'joke':
        if lang == 'en':
            greet_bot.send_message(last_chat_id, '''Ok, {}, I recorded. Now the owner will show it. 
            Will you write another one? If not, write PL, EN or RU and keep going.'''.format(usname))
        elif lang == 'ru':
            greet_bot.send_message(last_chat_id, '''Ok, {}, я записал. Теперь хозяину покажу это.
            Еще напишешь? Если нет, то пиши PL, EN или RU и едем дальше'''.format(usname))
        elif lang == 'pl':
            greet_bot.send_message(last_chat_id, '''Ok, {}, zapisałem ten. Teraz właścicielu go pokażę. 
            Czy chcesz pisać inny? Jeśli nie, to napisz PL, EN lub RU i lecimy dalej.'''.format(usname))


def tell_joke(lang, last_chatid): # get some joke from DB

    last_chatid = str(last_chatid)

    def get_from_db():
        with open(my_path+"jokes_"+lang+".csv", 'r') as rj:
            read = csv.reader(rj)
            joke_shown[last_chatid+'_'+lang] = list(read)
            return joke_shown[last_chatid+'_'+lang].pop()[3]

    try:
        if len(joke_shown[last_chatid+'_'+lang]) > 1:
            return joke_shown[last_chatid+'_'+lang].pop()[3]
        else:
            return get_from_db()

    except KeyError:
        return get_from_db()


def main():
    new_offset = None
    while True:
        get_result = greet_bot.get_updates(new_offset)

        if len(get_result) > 0:
            for j in get_result:
                get_message(j)
                new_offset = j['update_id'] + 1


        # for debugging:

        # now = datetime.datetime.now()
        # print('new_offset', new_offset, now.strftime("%H:%M:%S"))


greet_bot = BotHandler(token)

joke_shown = {} # for tell_joke()


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()
