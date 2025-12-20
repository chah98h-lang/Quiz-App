"""
Placeholder가 있는 문제들 찾기
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 로드
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

placeholder_questions = []

for q in data['questions']:
    # Dropdown 형식에서 placeholder 확인
    if 'options' in q and q['options']:
        for opt in q['options']:
            if 'PDF 참조' in opt.get('text', '') or 'PDF 이미지' in opt.get('text', ''):
                placeholder_questions.append(q['id'])
                break
    
    # Checkbox 형식에서 placeholder 확인
    if 'statements' in q and q['statements']:
        for stmt in q['statements']:
            if '이미지로 되어 있어' in str(stmt) or 'PDF 참조' in str(stmt):
                placeholder_questions.append(q['id'])
                break

print(f"Placeholder가 있는 문제: {len(placeholder_questions)}개")
print(f"문제 번호: {sorted(placeholder_questions)}")

