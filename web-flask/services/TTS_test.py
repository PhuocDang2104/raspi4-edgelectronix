import os

text = "Hello, this is a test of speech synthesis on Raspberry Pi."
# -v en+f3: chọn giọng nữ tiếng Anh
# -s 150: tốc độ vừa phải
# -a 200: max volume
cmd = f'espeak "{text}" -s 150 -a 200 -v en+f3'
os.system(cmd)