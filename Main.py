import speech_recognition as sr
import pyttsx3
import random
import re
from time import ctime
import time
from datetime import datetime
import webbrowser
import math
import subprocess
from weather import Weather, Unit
import requests
from bs4 import BeautifulSoup
import urllib3
import urllib
import urllib2
import threading

count_silence = 0
index_num = 0
urllib3.disable_warnings()
headers = 'Command,Results\n'

warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
#         speak cmd sing mLE




warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        
        
        
        
warning_dict = {'network_error': 'network  error,  please connect to the internet'}
names_id_det = {'friday_name': 'friday', 'user_name': 'B.Raghu'}
user_login = {'user_namee': 'Raghu', 'password': 123}
greetings = ['hi sir', 'Welcome boss']

speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')


'''for voice in voices:
    print(voice.id)'''

engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

'''---------------------Get-HTMl---------------------------'''


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return response.text


def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    result_block = soup.find_all('div', attrs={'class': 'Z0LcW'})
    multi_results_block = soup.find_all('div', attrs={'class': 'IAznY'})
    multi_results_block_1 = soup.find_all('div', attrs={'class': 'kltat'})
    result_block_3 = soup.find_all('div', attrs={'data-t': 'kno-desc-sh'})
    results_lyricks = soup.find_all('span', attrs={'jsname': 'YS01Ge'})
    result_wiki_msg = soup.find_all('div', attrs={'class': 'LGOjhe'})
    currency_cnv = soup.find_all('div', attrs={'class': 'dDoNo vk_bk'})

    if len(multi_results_block_1) > 0:
        print (len(multi_results_block_1))
        for er in range(0, len(multi_results_block_1)):
            name_is = multi_results_block_1[er].text
            speak_text_cmd(name_is)
            print(name_is)

    elif len(result_block) > 0:
        def file_save_record():
            filename = 'products.csv'
            f = open(filename, 'a', )
            f.write('\n' + voice_note + ',' + name_is.encode("utf-8"))
            f.close()
        try:
            name_is = result_block[0].text
            engine.setProperty('rate', 125)
            print(name_is)
            t1 = threading.Thread(target=file_save_record)
            t1.start()
            t1.join()
            speak_text_cmd(name_is)
            usrsaylst[index_num] = 0
            engine.setProperty('rate', 160)
        except IndexError:
            speak_text_cmd('something went problem , on google web scraping code')
            print('Index error try again..')

    elif len(multi_results_block) > 0:
        print (len(multi_results_block))
        if len(multi_results_block) > 0:
            for er in range(0, len(multi_results_block)):
                name_is = multi_results_block[er].text
                speak_text_cmd(name_is)
                print(name_is)

    elif len(result_wiki_msg) > 0:
        results_msg = result_wiki_msg[0].text
        print(results_msg)
        speak_text_cmd(results_msg)

    print len(result_block_3)
    if len(result_block_3) > 0 and usrsaylst[index_num] == 'what':
        name_is_2 = result_block_3[0].span.text
        print 'see results for'
        engine.setProperty('rate', 130)
        speak_text_cmd(name_is_2)
        engine.setProperty('rate', 160)
        print name_is_2

    if len(results_lyricks) > 0:
        for sre in range(0, len(results_lyricks)):
            name_is = results_lyricks[sre].text
            print(name_is)

    if len(currency_cnv) > 0:
        name_is = currency_cnv[0].text
        print(name_is)
        speak_text_cmd(name_is)


def speak_text_cmd(cmd):
    engine.say(cmd)
    engine.runAndWait()


def read_voice_cmd():
    voice_text = ''
    print('listening...')
    with sr.Microphone() as source:
        speech.adjust_for_ambient_noise(source)
        audio = speech.listen(source=source, timeout=6, phrase_time_limit=6)
    try:
        voice_text = str(speech.recognize_google(audio, language='en-IN'))
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print('network error.')
        speak_text_cmd(warning_dict['network_error'])
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text


def voice_act():
    voice_note_1 = read_voice_cmd()
    print 'cmd : {}'.format(voice_note_1.lower())
    if 'point break' == voice_note_1.lower():
        speak_text_cmd('welcome {}'.format('Raghu'))
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        speak_text_cmd('Voice activation required')
        activation = voice_act()
        checked_true = True
        checked_false = False
        if activation == checked_true:
            speak_text_cmd(random.choice(greetings))
            while True:
                try:
                    voice_note = read_voice_cmd()
                except sr.WaitTimeoutError:
                    continue
                voice_note = voice_note.lower()
                usrsaylst = voice_note.split(' ')
                print(' cmd : {} '.format(voice_note))
                try:
                    if voice_note == '':
                        continue
                    if len(usrsaylst) > 2:
                        try:
                            index_num = usrsaylst.index('play')
                            if usrsaylst[index_num] == 'play':
                                url = 'https://www.youtube.com/results?'
                                search_query = usrsaylst[index_num + 1:]
                                print(search_query)
                                args = urllib.urlencode({'search_query': search_query})
                                conn = urllib2.urlopen(url, args)
                                html_content = conn.read()
                                conn.close()
                                search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content)
                                webbrowser.open("https://www.youtube.com/watch?v=" + search_results[0])
                                speak_text_cmd('i got it sir, now you see there')
                                usrsaylst[index_num] = 0
                                break
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('who')
                            if usrsaylst[index_num] == 'who':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('how')
                            if usrsaylst[index_num] == 'how':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('what')
                            if usrsaylst[index_num] == 'what':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('convert')
                            if usrsaylst[index_num] == 'convert':
                                html = fetch_results(' '.join(usrsaylst[index_num:]), 10, 'en')
                                parse_results(html)
                                usrsaylst = voice_note.split(' ')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('photos')
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('images')
                            if usrsaylst[index_num] == 'images':
                                link = '+'.join(usrsaylst[index_num + 1:])
                                speak_text_cmd('just wait,  i will show images to you')
                                webbrowser.open(
                                    "https://www.google.co.in/search?hl=en&biw=1360&bih=662&tbm=isch&sa=1&ei=N6I3W6nWDsey9QPko6SYCA&q=" + link.lower())
                                continue
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                        try:
                            index_num = usrsaylst.index('map')
                            link = '+'.join(usrsaylst[index_num + 1:])
                            speak_text_cmd('holde on , i will show , to you')
                            webbrowser.open("https://www.google.co.in/maps/place/" + link + "/&amp;")
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    print usrsaylst
                    if voice_note == '':
                        count_silence = count_silence + 1
                        if count_silence == 9:
                            speak_text_cmd('i reminded ' + str(count_silence) + 'times')
                            count_silence = 0
                            time.sleep(60)
                        continue
                    elif 'local disk' in voice_note:
                        subprocess.call("explorer C:\\")
                        continue
                    elif 'what is your name' in voice_note:
                        speak_text_cmd('My name is ,  %s' % (names_id_det['friday_name']))
                        continue
                    elif 'weather in' in voice_note:
                        weather = Weather(unit=Unit.CELSIUS)
                        location = weather.lookup_by_location(voice_note[2:])
                        condition = location.condition
                        print(condition.text)
                        forecasts = location.forecast
                        for forecast in forecasts:
                            print(forecast.text)
                            print(forecast.date)
                            print(forecast.high)
                            print(forecast.low)
                        speak_text_cmd(condition.text)
                    elif 'now time' in voice_note:
                        print(ctime())
                        present = datetime.now()
                        print('Today date is', present.strftime('%d-%m-%Y'))
                        speak_text_cmd(ctime())
                        continue
                    elif usrsaylst[0] == 'exit' or usrsaylst[0] == 'close' or usrsaylst[0] == 'shutdown' or usrsaylst[
                        0] == 'by':
                        speak_text_cmd('ok program will be exit')
                        exit()
                    elif 'facebook' in voice_note:
                        speak_text_cmd('launching facebook on browser')
                        webbrowser.open("https://www.facebook.com/", new=1, autoraise=True)
                        continue
                    elif 'open' in voice_note:
                        subprocess.call("explorer C:\\Python27")
                        continue
                    if usrsaylst[0].lower() == 'search' or usrsaylst[0].lower() == 'find':
                        link = '+'.join(usrsaylst[1:])
                        speak_text_cmd('just wait,  i will search your task')
                        webbrowser.open("https://www.google.co.in/search?q=" + link.lower())
                        continue
                except IndexError:
                    print('Sorry Try again..')
                    pass
                except ValueError:
                    pass
        elif activation == checked_false:
            speak_text_cmd('Access Denied')
    except :
        print('Offline-mode')
        speak_text_cmd('offline mode')
        

