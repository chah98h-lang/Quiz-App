"""
50번 문제 확인
"""

import fitz
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf = fitz.open("AZ-900 영문 474.pdf")

all_text = ""
for page in pdf:
    all_text += page.get_text() + "\n"

pdf.close()

# Question #50 찾기
pattern = r'Question #50\n(.+?)Question #51'
match = re.search(pattern, all_text, re.DOTALL)

if match:
    q50_text = match.group(1)
    print("=" * 60)
    print("Question #50")
    print("=" * 60)
    print(q50_text[:1500])
else:
    print("Question #50를 찾을 수 없습니다.")

