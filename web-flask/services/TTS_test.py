import os

# Text to speak
text = "Hello, this is a test of speech synthesis on Raspberry Pi."

# Use espeak to play
os.system(f'espeak "{text}" -s 150 -a 200 -v en+f3')