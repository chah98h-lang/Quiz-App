"""
36번 문제 확인
"""

import fitz
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf = fitz.open("AZ-900 영문 474.pdf")

all_text = ""
for page in pdf:
    all_text += page.get_text() + "\n"

pdf.close()

# Question #36 찾기
import re
pattern = r'Question #36\n(.+?)Question #37'
match = re.search(pattern, all_text, re.DOTALL)

if match:
    q36_text = match.group(1)
    print("=" * 60)
    print("Question #36")
    print("=" * 60)
    print(q36_text[:2000])
else:
    print("Question #36를 찾을 수 없습니다.")

