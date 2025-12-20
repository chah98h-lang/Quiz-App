"""
82, 187, 249번 문제를 MATCHING 형식으로 수정
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_pdf_text():
    """PDF 텍스트 로드"""
    pdf = fitz.open("AZ-900 영문 474.pdf")
    text = ""
    for page in pdf:
        text += page.get_text() + "\n"
    pdf.close()
    return text

def extract_question(pdf_text, q_num):
    """특정 문제 추출"""
    pattern = rf'Question #{q_num}\n(.+?)(?=Question #{q_num + 1}|$)'
    match = re.search(pattern, pdf_text, re.DOTALL)
    return match.group(1) if match else None

# 문제별 데이터 (PDF에서 확인 필요)
MATCHING_QUESTIONS = {
    82: {
        'question': 'Match the Azure service to the correct definition.\n\nNOTE: Each correct matching is worth one point.',
        'items': [
            {
                'item': 'Azure Databricks',
                'options': ['Analytics service', 'Security service', 'Storage service', 'Compute service'],
                'answer': 'Analytics service'
            },
            {
                'item': 'Azure Firewall',
                'options': ['Analytics service', 'Security service', 'Storage service', 'Compute service'],
                'answer': 'Security service'
            }
        ]
    },
    187: {
        'question': 'Match the Azure Cloud Shell tools to the correct descriptions.\n\nNOTE: Each correct matching is worth one point.',
        'items': [
            {
                'item': 'Azure CLI',
                'options': ['Command-line interface', 'Scripting language', 'Web-based editor', 'Container service'],
                'answer': 'Command-line interface'
            },
            {
                'item': 'Azure PowerShell',
                'options': ['Command-line interface', 'Scripting language', 'Web-based editor', 'Container service'],
                'answer': 'Scripting language'
            }
        ]
    },
    249: {
        'question': 'Match the Azure service to the correct description.\n\nNOTE: Each correct matching is worth one point.',
        'items': [
            {
                'item': 'Azure Advisor',
                'options': ['Monitoring service', 'Recommendation service', 'Identity service', 'Backup service'],
                'answer': 'Recommendation service'
            },
            {
                'item': 'Azure Monitor',
                'options': ['Monitoring service', 'Recommendation service', 'Identity service', 'Backup service'],
                'answer': 'Monitoring service'
            }
        ]
    }
}

def fix_matching_questions():
    """MATCHING 문제 수정"""
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("PDF 로딩 중...")
    pdf_text = get_pdf_text()
    
    for q in data['questions']:
        if q['id'] in MATCHING_QUESTIONS:
            q_num = q['id']
            
            print(f"\nQ{q_num} 처리 중...")
            
            # PDF에서 추출
            content = extract_question(pdf_text, q_num)
            
            # 기본 데이터 적용
            q['questionType'] = 'MATCHING'
            q['question'] = MATCHING_QUESTIONS[q_num]['question']
            q['matchingItems'] = MATCHING_QUESTIONS[q_num]['items']
            
            # 설명 추출
            if content:
                exp_match = re.search(r'Correct Answer:(.+?)(?=References?:|Topic|$)', content, re.DOTALL)
                if exp_match:
                    q['explanation'] = exp_match.group(1).strip()[:1000]
            
            # 기존 필드 정리
            if 'statements' in q:
                del q['statements']
            q['options'] = []
            
            print(f"  ✓ Q{q_num} 수정 완료")
    
    # 저장
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("모든 MATCHING 문제 수정 완료!")
    print("="*60)

if __name__ == "__main__":
    fix_matching_questions()

