"""
365번 문제 간단하게 수정
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
        q['questionType'] = 'MATCHING'
        q['question'] = 'How should you calculate the monthly uptime percentage?\n\nFormula: A / B × C\n\nTo answer, select the appropriate options for A, B, and C.\n\nNOTE: Each correct selection is worth one point.'
        
        q['matchingItems'] = [
            {
                'item': 'A',
                'options': [
                    'Downtime in Minutes',
                    'Maximum Available Minutes',
                    '(Maximum Available Minutes - Downtime in Minutes)'
                ],
                'answer': '(Maximum Available Minutes - Downtime in Minutes)'
            },
            {
                'item': 'B',
                'options': [
                    '60',
                    '1,440',
                    'Maximum Available Minutes'
                ],
                'answer': 'Maximum Available Minutes'
            },
            {
                'item': 'C',
                'options': [
                    '100',
                    '99.99',
                    '1.440'
                ],
                'answer': '100'
            }
        ]
        
        q['explanation'] = 'Monthly Uptime % = (Maximum Available Minutes - Downtime in Minutes) / Maximum Available Minutes × 100\n\nA = (Maximum Available Minutes - Downtime in Minutes)\nB = Maximum Available Minutes\nC = 100'
        
        # 기존 필드 정리
        if 'statements' in q:
            del q['statements']
        q['options'] = []
        
        print("365번 문제 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

