import speech_recognition as sr
import pyttsx3
import random
speech = sr.Recognizer()
try:
    engine = pyttsx3.init('sapi5')
except ImportError:
    print('Requsted driver not found')
except RuntimeError:
    print('Driver fails to initialize')

voices = engine.getProperty('voices')

for voice in voices:
    print(voice.id)

'''engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MS-Anna-1033-20-DSK')
rate = engine.getProperty('rate')
engine.setProperty('rate', 160)'''


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
        speak_text_cmd('Network Error')
        exit()
    except sr.WaitTimeoutError:
        print 'i could not hear anything'
        pass
    return voice_text

read_voice_cmd()  
