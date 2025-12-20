"""
Placeholder 문제들을 MULTIPLE_CHOICE로 변환
드롭다운이 앞/뒤에 있는 경우만 처리
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_pdf_text():
    """PDF 텍스트 로드"""
    print("PDF 로딩 중...")
    pdf = fitz.open("AZ-900 영문 474.pdf")
    text = ""
    for page in pdf:
        text += page.get_text() + "\n"
    pdf.close()
    return text

def extract_question(pdf_text, q_num):
    """특정 문제 추출"""
    pattern = rf'Question #{q_num}\n(.+?)(?=Question #{q_num + 1}|Topic \d+|$)'
    match = re.search(pattern, pdf_text, re.DOTALL)
    return match.group(1) if match else None

def analyze_dropdown_position(content):
    """
    드롭다운 위치 분석
    Returns: ('front', 'back', 'middle', or None)
    """
    
    # HOTSPOT 관련 키워드 찾기
    if 'HOTSPOT' not in content.upper():
        return None
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    # "To complete the sentence" 다음의 문장 찾기
    sentence = None
    for i, line in enumerate(lines):
        if 'complete the sentence' in line.lower():
            # 다음 몇 줄을 확인
            for j in range(i+1, min(i+5, len(lines))):
                if len(lines[j]) > 30 and not lines[j].startswith('Answer'):
                    sentence = lines[j]
                    break
            break
    
    if not sentence:
        # Hot Area 다음 문장 찾기
        for i, line in enumerate(lines):
            if 'Hot Area' in line or 'Answer Area' in line:
                for j in range(i+1, min(i+5, len(lines))):
                    if len(lines[j]) > 30:
                        sentence = lines[j]
                        break
                break
    
    if not sentence:
        return None
    
    print(f"  문장: {sentence[:100]}...")
    
    # 빈칸 패턴 찾기
    # 보통 "______" 또는 "___" 형태
    blank_patterns = [
        r'^_{3,}',  # 시작에 빈칸
        r'_{3,}$',  # 끝에 빈칸
        r'\s_{3,}\s',  # 중간에 빈칸
    ]
    
    if re.search(blank_patterns[0], sentence):
        return 'front'
    elif re.search(blank_patterns[1], sentence):
        return 'back'
    elif re.search(blank_patterns[2], sentence):
        return 'middle'
    
    # 빈칸이 명시적으로 없는 경우, 문장 구조로 판단
    # "... must plan to" -> 뒤에 올 것
    # "... you can" -> 뒤에 올 것
    back_indicators = [
        r'must plan to$',
        r'you can$',
        r'should$',
        r'to$',
        r'will$',
    ]
    
    for pattern in back_indicators:
        if re.search(pattern, sentence.strip()):
            return 'back'
    
    return None

def extract_options_from_explanation(content):
    """해설에서 선택지 추출"""
    
    # Correct Answer 찾기
    answer_match = re.search(r'Correct Answer:\s*([A-Z])', content)
    answer = answer_match.group(1) if answer_match else 'B'
    
    # 해설 추출
    explanation = ""
    exp_match = re.search(r'Correct Answer:(.+?)(?=References?:|Topic|Question|$)', content, re.DOTALL)
    if exp_match:
        explanation = exp_match.group(1).strip()
    
    # 드롭다운 선택지 패턴 찾기
    # 보통 리스트 형태로 나열됨
    options_text = []
    
    # 패턴 1: 줄바꿈으로 구분된 선택지
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # 짧은 문장들 (선택지일 가능성)
        if 10 < len(line) < 150 and not line.startswith('Question') and not line.startswith('Topic'):
            # 특정 키워드 포함
            if any(word in line.lower() for word in ['azure', 'cloud', 'data', 'region', 'zone', 'service']):
                if line not in options_text:
                    options_text.append(line)
    
    # 상위 4개만 선택
    options_text = options_text[:4]
    
    if len(options_text) < 4:
        # 기본 옵션
        options_text = [
            'Option A (PDF 참조)',
            'Option B (PDF 참조)',
            'Option C (PDF 참조)',
            'Option D (PDF 참조)'
        ]
    
    options = []
    for i, text in enumerate(options_text):
        options.append({
            'letter': chr(65 + i),
            'text': text
        })
    
    return options, answer, explanation

def process_all_questions():
    """모든 문제 처리"""
    
    pdf_text = get_pdf_text()
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_ids = [40, 104, 115, 118, 126, 132, 188, 212, 219, 230, 231, 232, 
                  251, 265, 281, 296, 297, 298, 299, 306, 310, 329, 338, 372, 403]
    
    # 40번은 이미 처리됨
    target_ids.remove(40)
    
    converted = []
    middle_questions = []
    failed = []
    
    for q_id in target_ids:
        print(f"\n{'='*60}")
        print(f"Q{q_id} 처리 중...")
        
        # PDF에서 추출
        content = extract_question(pdf_text, q_id)
        if not content:
            print(f"  ✗ PDF에서 찾을 수 없음")
            failed.append(q_id)
            continue
        
        # 드롭다운 위치 분석
        position = analyze_dropdown_position(content)
        
        if position is None:
            print(f"  ✗ 드롭다운 위치를 찾을 수 없음")
            failed.append(q_id)
            continue
        
        if position == 'middle':
            print(f"  ⚠ 드롭다운이 중간에 있음 - 건너뜀")
            middle_questions.append(q_id)
            continue
        
        print(f"  드롭다운 위치: {position}")
        
        # 선택지 추출
        options, answer, explanation = extract_options_from_explanation(content)
        
        # JSON에서 해당 문제 찾아서 수정
        for q in data['questions']:
            if q['id'] == q_id:
                # 문장에 빈칸 추가
                question_text = q.get('question', '')
                
                if position == 'front':
                    question_text = "_______ " + question_text
                elif position == 'back':
                    if not question_text.endswith('_'):
                        question_text = question_text.rstrip() + " _______"
                
                q['question'] = question_text
                q['questionType'] = 'MULTIPLE_CHOICE'
                q['options'] = options
                q['answer'] = answer
                q['explanation'] = explanation[:800] if explanation else q.get('explanation', '')
                
                # dropdowns 제거
                if 'dropdowns' in q:
                    del q['dropdowns']
                
                converted.append(q_id)
                print(f"  ✓ MULTIPLE_CHOICE로 변환 완료")
                break
    
    # 저장
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"변환 완료: {len(converted)}개")
    print(f"중간 드롭다운 (건너뜀): {len(middle_questions)}개")
    print(f"실패: {len(failed)}개")
    
    if middle_questions:
        print(f"\n⚠ 드롭다운이 중간에 있는 문제들:")
        print(f"   {middle_questions}")
    
    if failed:
        print(f"\n✗ 처리 실패한 문제들:")
        print(f"   {failed}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    process_all_questions()

