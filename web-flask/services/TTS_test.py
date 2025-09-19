import os

text = "Hello, this is a clearer test with e-speak NG."
os.system(f'espeak-ng "{text}" -s 150 -a 200 -v en+f3')