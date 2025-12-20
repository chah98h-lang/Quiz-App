"""
46번 문제 수정 - 2개 드롭박스 형식
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
        # HOTSPOT 형식으로 변경 (각 항목별 선택)
        q['questionType'] = 'HOTSPOT'
        q['question'] = 'Which cloud deployment solution is used for Azure virtual machines and Azure SQL databases?\n\nNOTE: Each correct selection is worth one point.'
        q['statements'] = [
            'Azure virtual machines use Infrastructure as a Service (IaaS)',
            'Azure SQL databases use Platform as a Service (PaaS)'
        ]
        q['answer'] = ['Yes', 'Yes']
        q['explanation'] = 'Azure virtual machines are Infrastructure as a Service (IaaS). Azure SQL databases are Platform as a Service (PaaS).'
        q['options'] = []
        
        print("46번 문제 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

