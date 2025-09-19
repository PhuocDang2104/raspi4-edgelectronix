import os

# Câu muốn đọc
text = "Xin chào, đây là thử nghiệm phát âm thanh trên Raspberry Pi."

# Dùng espeak để phát
os.system(f'espeak "{text}" -s 150 -v vi+f3')  
# -s: speed (150 từ/phút), -v: voice (vi: tiếng Việt, f3: female voice)
