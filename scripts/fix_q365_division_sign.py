"""
365번 문제 - 나누기 기호 수정
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 로드
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 365번 문제 찾기
for q in data['questions']:
    if q['id'] == 365:
        q['question'] = 'How should you calculate the monthly uptime percentage?\n\nFormula: A ÷ B × C\n\nTo answer, select the appropriate options for A, B, and C.\n\nNOTE: Each correct selection is worth one point.'
        
        print("365번 문제 나누기 기호 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

