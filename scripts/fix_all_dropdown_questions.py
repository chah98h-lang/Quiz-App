"""
모든 Dropdown placeholder 문제 수정
PDF에서 실제 내용 추출
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 문제별 매핑 데이터 (수동으로 확인한 주요 문제들)
QUESTION_FIXES = {
    40: {
        'question': 'Match the Azure service to the correct description.\n\nInstructions: To answer, drag the appropriate Azure service from the column on the left to its description on the right.',
        'type': 'matching'
    },
    38: {
        'question': 'An organization that hosts its infrastructure _______ no longer requires a data center.',
        'options': [
            'in a private cloud',
            'in a hybrid cloud',
            'in the public cloud',
            'on a Hyper-V host'
        ],
        'answer_index': 2  # C
    }
}

def load_pdf():
    """PDF 로드"""
    pdf = fitz.open("AZ-900 영문 474.pdf")
    text = ""
    for page in pdf:
        text += page.get_text() + "\n"
    pdf.close()
    return text

def extract_question_content(pdf_text, q_num):
    """특정 문제 번호의 내용 추출"""
    pattern = rf'Question #{q_num}\n(.+?)(?=Question #{q_num + 1}|$)'
    match = re.search(pattern, pdf_text, re.DOTALL)
    return match.group(1) if match else None

def parse_dropdown_from_content(content):
    """Content에서 dropdown 정보 파싱"""
    
    # Correct Answer 찾기
    answer_match = re.search(r'Correct Answer:\s*(.+?)(?=\n\n|References?:|Topic|$)', content, re.DOTALL)
    if not answer_match:
        return None
    
    answer_section = answer_match.group(1).strip()
    
    # 첫 글자가 정답 (A, B, C, D)
    answer_letter = answer_section[0] if answer_section and answer_section[0] in 'ABCD' else 'A'
    
    # 해설에서 선택지 추출 시도
    options = extract_options_from_explanation(content, answer_section)
    
    # 문장 패턴 찾기
    question = extract_sentence_pattern(content)
    
    if options and len(options) >= 2:
        return {
            'question': question,
            'options': options,
            'answer': answer_letter,
            'explanation': answer_section[:500]
        }
    
    return None

def extract_options_from_explanation(content, answer_section):
    """해설에서 선택지 추출"""
    
    options = []
    
    # 일반적인 패턴들
    patterns = [
        # Cloud 관련
        r'((?:in |on )?(?:a |the )?(?:private|public|hybrid) cloud)',
        # Service 모델
        r'((?:Software|Platform|Infrastructure) as a Service(?: \((?:SaaS|PaaS|IaaS)\))?)',
        # Azure 서비스
        r'(Azure [A-Z][a-z]+(?: [A-Z][a-z]+)*)',
    ]
    
    found = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            match = match.strip()
            if len(match) > 3 and len(match) < 100:
                found.add(match)
    
    # 4개 이상이면 처음 4개만
    if len(found) >= 2:
        sorted_options = sorted(list(found))[:4]
        for i, opt in enumerate(sorted_options):
            options.append({
                'letter': chr(65 + i),
                'text': opt
            })
        return options
    
    return None

def extract_sentence_pattern(content):
    """빈칸이 있는 문장 추출"""
    
    # 첫 몇 줄에서 문장 찾기
    lines = content.split('\n')[:10]
    
    for line in lines:
        line = line.strip()
        # 의미있는 문장이고 충분히 긴 경우
        if len(line) > 30 and ('?' in line or '.' in line):
            # HOTSPOT, DRAG DROP 등 키워드 제거
            line = re.sub(r'HOTSPOT\s*-?\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'To complete the sentence.*?area\.', '', line, flags=re.IGNORECASE)
            line = line.strip()
            if line:
                return line
    
    return "To complete the sentence, select the appropriate option."

def fix_all_placeholders(pdf_text, json_path):
    """모든 placeholder 문제 수정"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed_count = 0
    failed = []
    
    for q in data['questions']:
        # Placeholder 확인
        has_placeholder = False
        if 'options' in q:
            for opt in q.get('options', []):
                if 'PDF 참조' in opt.get('text', ''):
                    has_placeholder = True
                    break
        
        if not has_placeholder:
            continue
        
        q_num = q['id']
        print(f"Q{q_num} 처리 중...")
        
        # PDF에서 추출
        content = extract_question_content(pdf_text, q_num)
        if not content:
            print(f"  - PDF에서 찾을 수 없음")
            failed.append(q_num)
            continue
        
        # 파싱
        parsed = parse_dropdown_from_content(content)
        
        if parsed:
            q['question'] = parsed['question']
            q['options'] = parsed['options']
            q['answer'] = parsed['answer']
            q['explanation'] = parsed['explanation']
            fixed_count += 1
            print(f"  ✓ 수정 완료")
        else:
            print(f"  - 파싱 실패")
            failed.append(q_num)
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"수정 완료: {fixed_count}개")
    print(f"실패: {len(failed)}개 - {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("PDF 로딩 중...")
    pdf_text = load_pdf()
    
    print("문제 수정 중...")
    fix_all_placeholders(pdf_text, "quiz_data.json")
    
    print("\n완료!")

