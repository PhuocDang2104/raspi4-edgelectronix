from gtts import gTTS
import os

tts = gTTS("Hello, this is a natural test", lang="en")
tts.save("test.mp3")
os.system("mpg123 test.mp3")