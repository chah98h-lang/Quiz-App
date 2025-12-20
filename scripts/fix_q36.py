"""
36번 문제 수정
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 로드
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 36번 문제 찾기
for q in data['questions']:
    if q['id'] == 36:
        q['question'] = "To complete the sentence, select the appropriate option in the answer area.\n\nWhen you are implementing a _______ solution, you are responsible for configuring the solution. Everything else is managed by the cloud provider."
        q['options'] = [
            {"letter": "A", "text": "Software as a Service (SaaS)"},
            {"letter": "B", "text": "Platform as a Service (PaaS)"},
            {"letter": "C", "text": "Infrastructure as a Service (IaaS)"},
            {"letter": "D", "text": "Serverless computing"}
        ]
        q['answer'] = "A"
        q['explanation'] = "When you are implementing a Software as a Service (SaaS) solution, you are responsible for configuring the SaaS solution. Everything else is managed by the cloud provider. SaaS requires the least amount of management. The cloud provider is responsible for managing everything, and the end user just uses the software."
        print("36번 문제 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

