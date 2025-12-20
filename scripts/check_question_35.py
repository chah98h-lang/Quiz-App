"""
35번 문제 확인
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

# Question #35 찾기
import re
pattern = r'Question #35\n(.+?)Question #36'
match = re.search(pattern, all_text, re.DOTALL)

if match:
    q35_text = match.group(1)
    print("=" * 60)
    print("Question #35")
    print("=" * 60)
    print(q35_text[:2000])
else:
    print("Question #35를 찾을 수 없습니다.")

