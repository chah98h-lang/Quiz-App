"""
50번 문제 수정
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON 로드
with open('quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 50번 문제 찾기
for q in data['questions']:
    if q['id'] == 50:
        q['questionType'] = 'MULTIPLE_CHOICE'
        q['question'] = 'To complete the sentence, select the appropriate option in the answer area.\n\nAzure Site Recovery provides _______ for virtual machines.'
        
        q['options'] = [
            {"letter": "A", "text": "fault tolerance"},
            {"letter": "B", "text": "disaster recovery"},
            {"letter": "C", "text": "elasticity"},
            {"letter": "D", "text": "high availability"}
        ]
        
        q['answer'] = 'B'
        q['explanation'] = 'Azure Site Recovery helps ensure business continuity by keeping business apps and workloads running during outages. Site Recovery replicates workloads running on physical and virtual machines (VMs) from a primary site to a secondary location.'
        
        print("50번 문제 수정 완료!")
        break

# 저장
with open('quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("저장 완료!")

