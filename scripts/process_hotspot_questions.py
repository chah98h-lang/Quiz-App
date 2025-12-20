"""
모든 HOTSPOT/HOT_AREA 문제 자동 처리
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 제외할 문제
EXCLUDE_IDS = [97, 109, 112, 168, 199, 215, 276, 328]

def load_pdf_text(pdf_path):
    """PDF 전체 텍스트 로드"""
    pdf = fitz.open(pdf_path)
    all_text = ""
    for page in pdf:
        all_text += page.get_text() + "\n"
    pdf.close()
    return all_text

def extract_question_from_pdf(all_text, q_num):
    """특정 문제 번호의 텍스트 추출"""
    pattern = rf'Question #{q_num}\n(.+?)Question #{q_num + 1}'
    match = re.search(pattern, all_text, re.DOTALL)
    if match:
        return match.group(1)
    
    # 마지막 문제인 경우
    pattern = rf'Question #{q_num}\n(.+?)$'
    match = re.search(pattern, all_text, re.DOTALL)
    if match:
        return match.group(1)
    
    return None

def classify_hotspot_type(content):
    """HOTSPOT 문제 타입 분류
    
    Returns:
        'checkbox': Yes/No statements 형식
        'dropdown': 빈칸 채우기 형식
        'unknown': 판단 불가
    """
    content_upper = content.upper()
    
    # Checkbox 형식 키워드
    checkbox_keywords = [
        'SELECT YES IF THE STATEMENT IS TRUE',
        'SELECT NO IF',
        'FOR EACH OF THE FOLLOWING STATEMENTS',
        'EACH CORRECT SELECTION IS WORTH ONE POINT'
    ]
    
    # Dropdown 형식 키워드
    dropdown_keywords = [
        'TO COMPLETE THE SENTENCE',
        'SELECT THE APPROPRIATE OPTION',
        'ANSWER AREA'
    ]
    
    checkbox_score = sum(1 for kw in checkbox_keywords if kw in content_upper)
    dropdown_score = sum(1 for kw in dropdown_keywords if kw in content_upper)
    
    if checkbox_score > dropdown_score:
        return 'checkbox'
    elif dropdown_score > checkbox_score:
        return 'dropdown'
    else:
        # Box 1, Box 2, Box 3 패턴 확인
        if re.search(r'Box \d+:', content):
            return 'checkbox'
        return 'unknown'

def parse_checkbox_question(q_num, content):
    """Checkbox 형식 파싱"""
    
    # 정답 추출 (Box 1: Yes, Box 2: No, Box 3: Yes)
    answers = []
    for i in range(1, 6):  # 최대 5개까지
        match = re.search(rf'Box {i}:\s*(Yes|No)', content, re.IGNORECASE)
        if match:
            answers.append(match.group(1).capitalize())
        else:
            break
    
    if not answers:
        return None
    
    # Statements는 해설에서 유추 (간단한 버전)
    statements = []
    for i in range(len(answers)):
        statements.append(f"Statement {i+1} (이미지로 되어 있어 텍스트 추출 불가)")
    
    # 해설 추출
    explanation = ""
    exp_match = re.search(r'(?:References?|Explanation):\s*(.+?)(?=Topic|$)', content, re.DOTALL | re.IGNORECASE)
    if exp_match:
        explanation = exp_match.group(1).strip()[:1000]
    
    return {
        'questionType': 'HOTSPOT',
        'question': 'For each of the following statements, select Yes if the statement is true. Otherwise, select No.',
        'statements': statements,
        'answer': answers,
        'explanation': explanation
    }

def parse_dropdown_question(q_num, content):
    """Dropdown 형식 파싱"""
    
    # 빈칸 문장 찾기 (일반적으로 간단한 문장)
    # 정답에서 유추
    answer_match = re.search(r'Correct Answer:\s*(.+)', content)
    if not answer_match:
        return None
    
    answer_text = answer_match.group(1).strip()
    
    # 선택지는 해설에서 추출하거나 기본값 사용
    # (간단한 버전 - 실제로는 더 복잡한 파싱 필요)
    
    return {
        'questionType': 'MULTIPLE_CHOICE',
        'question': 'To complete the sentence, select the appropriate option. (빈칸 문장은 PDF 이미지 참조)',
        'options': [
            {'letter': 'A', 'text': 'Option A (PDF 참조)'},
            {'letter': 'B', 'text': 'Option B (PDF 참조)'},
            {'letter': 'C', 'text': 'Option C (PDF 참조)'},
            {'letter': 'D', 'text': 'Option D (PDF 참조)'}
        ],
        'answer': answer_text[0] if answer_text else 'A',
        'explanation': answer_text
    }

def process_all_hotspot_questions(pdf_path, json_path):
    """모든 HOTSPOT 문제 처리"""
    
    print("PDF 로딩 중...")
    pdf_text = load_pdf_text(pdf_path)
    
    print("JSON 로딩 중...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # HOTSPOT/HOT_AREA 문제 찾기
    hotspot_questions = [q for q in data['questions'] 
                        if q.get('questionType') in ['HOTSPOT', 'HOT_AREA']]
    
    print(f"\n전체 HOTSPOT/HOT_AREA 문제: {len(hotspot_questions)}개")
    print(f"제외할 문제: {EXCLUDE_IDS}")
    
    # 처리할 문제 필터링
    target_questions = [q for q in hotspot_questions if q['id'] not in EXCLUDE_IDS]
    print(f"처리할 문제: {len(target_questions)}개")
    
    # 각 문제 처리
    updated_count = 0
    checkbox_count = 0
    dropdown_count = 0
    unknown_count = 0
    
    for q in target_questions:
        q_num = q['id']
        
        # PDF에서 문제 텍스트 추출
        content = extract_question_from_pdf(pdf_text, q_num)
        if not content:
            print(f"Q{q_num}: PDF에서 찾을 수 없음")
            unknown_count += 1
            continue
        
        # 타입 분류
        q_type = classify_hotspot_type(content)
        
        if q_type == 'checkbox':
            parsed = parse_checkbox_question(q_num, content)
            if parsed:
                q.update(parsed)
                checkbox_count += 1
                updated_count += 1
                print(f"Q{q_num}: Checkbox 형식 처리 완료")
        
        elif q_type == 'dropdown':
            parsed = parse_dropdown_question(q_num, content)
            if parsed:
                q.update(parsed)
                dropdown_count += 1
                updated_count += 1
                print(f"Q{q_num}: Dropdown 형식 처리 완료")
        
        else:
            print(f"Q{q_num}: 타입 판단 불가")
            unknown_count += 1
    
    # JSON 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"처리 완료!")
    print(f"  Checkbox 형식: {checkbox_count}개")
    print(f"  Dropdown 형식: {dropdown_count}개")
    print(f"  타입 불명: {unknown_count}개")
    print(f"  총 업데이트: {updated_count}개")
    print("=" * 60)

if __name__ == "__main__":
    pdf_file = "AZ-900 영문 474.pdf"
    json_file = "quiz_data.json"
    
    process_all_hotspot_questions(pdf_file, json_file)

