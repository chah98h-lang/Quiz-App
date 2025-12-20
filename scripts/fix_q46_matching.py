"""
46번 문제 - Matching 형식으로 수정
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 로드
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 46번 문제 찾기
for q in data['questions']:
    if q['id'] == 46:
        q['questionType'] = 'MATCHING'
        q['question'] = 'Which cloud deployment solution is used for Azure virtual machines and Azure SQL databases?\n\nNOTE: Each correct selection is worth one point.'
        
        # Matching 형식: 각 항목과 선택지
        q['matchingItems'] = [
            {
                'item': 'Azure virtual machines',
                'options': ['Infrastructure as a Service (IaaS)', 'Platform as a Service (PaaS)', 'Software as a Service (SaaS)'],
                'answer': 'Infrastructure as a Service (IaaS)'
            },
            {
                'item': 'Azure SQL databases',
                'options': ['Infrastructure as a Service (IaaS)', 'Platform as a Service (PaaS)', 'Software as a Service (SaaS)'],
                'answer': 'Platform as a Service (PaaS)'
            }
        ]
        
        q['explanation'] = 'Azure virtual machines are an example of Infrastructure as a Service (IaaS). Azure SQL databases are an example of Platform as a Service (PaaS).'
        
        # 기존 필드 제거
        if 'statements' in q:
            del q['statements']
        if 'options' in q:
            q['options'] = []
        
        print("46번 문제 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

