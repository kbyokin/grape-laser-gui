from gtts import gTTS
import os

my_text = 'ベリーを切ってください。'
language = 'ja'

myobj = gTTS(text=my_text, lang=language, slow=False, )
myobj.save('./mp3/cutberry.mp3')

os.system("mpg321 ./mp3/cutberry.mp3")