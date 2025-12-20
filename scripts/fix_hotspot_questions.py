"""
HOTSPOT 문제 재파싱 스크립트
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_hotspot_questions(pdf_path):
    """HOTSPOT 문제만 추출"""
    
    pdf = fitz.open(pdf_path)
    all_text = ""
    
    print("PDF 읽는 중...")
    for page_num in range(pdf.page_count):
        all_text += pdf[page_num].get_text() + "\n"
    
    pdf.close()
    
    # Question #X 패턴으로 분리
    questions_raw = re.split(r'Question #(\d+)', all_text)
    
    hotspot_questions = []
    
    for i in range(1, len(questions_raw), 2):
        if i + 1 >= len(questions_raw):
            break
        
        q_num = questions_raw[i]
        q_content = questions_raw[i + 1]
        
        # HOTSPOT 문제만 처리
        if 'HOTSPOT' in q_content.upper():
            parsed = parse_hotspot_question(int(q_num), q_content)
            if parsed:
                hotspot_questions.append(parsed)
                print(f"Q{q_num} - HOTSPOT 파싱 완료")
    
    return hotspot_questions


def parse_hotspot_question(q_num, content):
    """HOTSPOT 문제 파싱"""
    
    lines = content.strip().split('\n')
    
    # 기본 정보
    q_data = {
        "id": q_num,
        "original_number": str(q_num),
        "questionType": "HOTSPOT",
        "question": "",
        "statements": [],
        "answer": ""
    }
    
    # 질문 텍스트 추출 (HOTSPOT 다음부터 statement 또는 Correct Answer 전까지)
    question_lines = []
    statement_started = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # HOTSPOT 키워드 건너뛰기
        if 'HOTSPOT' in line.upper():
            continue
        
        # Correct Answer 이전까지
        if 'Correct Answer' in line:
            break
        
        # Statement 패턴 감지
        if any(keyword in line for keyword in ['Select Yes if', 'Select No if', 'For each of the following']):
            statement_started = True
        
        if not statement_started:
            question_lines.append(line)
    
    q_data["question"] = ' '.join(question_lines)[:1000]
    
    # Statements 추출 (여러 패턴 시도)
    statements = extract_statements_from_content(content)
    
    if statements:
        q_data["statements"] = statements
        
        # 정답 추출
        answer_match = re.search(r'Correct Answer:\s*(.+)', content)
        if answer_match:
            answer_text = answer_match.group(1).strip()
            q_data["answer"] = parse_hotspot_answer(answer_text, len(statements))
    
    return q_data if statements else None


def extract_statements_from_content(content):
    """Content에서 statement 추출"""
    
    statements = []
    
    # 패턴 1: "Statement text" 형태
    # 일반적으로 3개의 statement가 연속으로 나옴
    lines = content.split('\n')
    
    collecting = False
    current_statement = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Yes/No가 나오면 statement 영역
        if 'Yes' in line and 'No' in line and len(line) < 20:
            collecting = True
            if current_statement:
                statements.append(' '.join(current_statement))
                current_statement = []
            continue
        
        # Correct Answer가 나오면 종료
        if 'Correct Answer' in line:
            if current_statement:
                statements.append(' '.join(current_statement))
            break
        
        # Statement 수집
        if collecting and line:
            # 너무 짧거나 불필요한 줄 제외
            if len(line) > 10 and not line.startswith('Reference'):
                current_statement.append(line)
                
                # 문장이 완성되면 추가 (마침표로 끝나거나 충분히 긴 경우)
                if line.endswith('.') or len(' '.join(current_statement)) > 50:
                    statements.append(' '.join(current_statement))
                    current_statement = []
    
    # 최대 5개까지만 (보통 3개)
    return statements[:5] if statements else []


def parse_hotspot_answer(answer_text, num_statements):
    """정답 파싱"""
    
    # Yes/No 패턴 찾기
    answers = []
    
    # "Yes, No, Yes" 형태
    if ',' in answer_text:
        parts = answer_text.split(',')
        for part in parts[:num_statements]:
            part = part.strip().upper()
            if 'YES' in part:
                answers.append('Yes')
            elif 'NO' in part:
                answers.append('No')
    else:
        # 텍스트에서 Yes/No 찾기
        for i in range(num_statements):
            if 'YES' in answer_text.upper():
                answers.append('Yes')
            else:
                answers.append('No')
    
    return answers if answers else ['Yes'] * num_statements


def update_json_with_hotspot(json_path, hotspot_questions):
    """기존 JSON에 HOTSPOT 문제 업데이트"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # HOTSPOT 문제 ID 매핑
    hotspot_map = {q['id']: q for q in hotspot_questions}
    
    # 기존 문제 업데이트
    updated_count = 0
    for q in data['questions']:
        if q['id'] in hotspot_map and q.get('questionType') == 'HOTSPOT':
            hotspot_data = hotspot_map[q['id']]
            q['statements'] = hotspot_data['statements']
            q['answer'] = hotspot_data['answer']
            if hotspot_data['question']:
                q['question'] = hotspot_data['question']
            updated_count += 1
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return updated_count


if __name__ == "__main__":
    print("=" * 60)
    print("HOTSPOT 문제 재파싱")
    print("=" * 60)
    
    pdf_file = "AZ-900 영문 474.pdf"
    json_file = "quiz_data.json"
    
    # HOTSPOT 문제 추출
    hotspot_qs = extract_hotspot_questions(pdf_file)
    
    print(f"\n추출된 HOTSPOT 문제: {len(hotspot_qs)}개")
    
    # JSON 업데이트
    updated = update_json_with_hotspot(json_file, hotspot_qs)
    
    print(f"업데이트된 문제: {updated}개")
    print("\n완료!")

