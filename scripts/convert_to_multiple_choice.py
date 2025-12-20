"""
Placeholder 문제들을 MULTIPLE_CHOICE로 변환 (문장 끝 빈칸)
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

def parse_hotspot_dropdown(content, q_num):
    """HOTSPOT 드롭다운 문제 파싱"""
    
    # Correct Answer 추출
    answer_match = re.search(r'Correct Answer:\s*([A-D])', content)
    answer_letter = answer_match.group(1) if answer_match else 'B'
    
    # 해설 추출
    explanation = ""
    exp_match = re.search(r'Correct Answer:.*?\n(.+?)(?=Reference|Topic|Question|$)', content, re.DOTALL)
    if exp_match:
        explanation = exp_match.group(1).strip()[:800]
    
    # 문장 찾기 (Answer Area 이후)
    sentence = None
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    in_answer_area = False
    for i, line in enumerate(lines):
        if 'Answer Area' in line or 'Hot Area' in line:
            in_answer_area = True
            continue
        
        if in_answer_area and len(line) > 20:
            # 긴 문장 찾기
            if not line.startswith('Correct') and not line.startswith('Reference'):
                sentence = line
                break
    
    # 선택지 찾기 (드롭다운 내용)
    options = []
    option_lines = []
    
    # Answer Area와 Correct Answer 사이에서 선택지 추출
    in_options = False
    for line in lines:
        if 'Answer Area' in line:
            in_options = True
            continue
        if 'Correct Answer' in line:
            in_options = False
            break
        
        if in_options and 5 < len(line) < 200:
            # URL이나 특정 키워드 제외
            if not line.startswith('http') and not line.startswith('Reference'):
                if line not in option_lines and line != sentence:
                    option_lines.append(line)
    
    # 옵션이 충분하면 사용
    if len(option_lines) >= 3:
        for i, opt in enumerate(option_lines[:4]):
            options.append({
                'letter': chr(65 + i),
                'text': opt
            })
    
    # 옵션이 부족하면 기본값
    while len(options) < 4:
        options.append({
            'letter': chr(65 + len(options)),
            'text': f'Option {chr(65 + len(options))} (PDF 참조)'
        })
    
    return sentence, options, answer_letter, explanation

def convert_all_questions():
    """모든 문제 변환"""
    
    pdf_text = get_pdf_text()
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_ids = [104, 115, 118, 126, 132, 188, 212, 219, 230, 231, 232, 
                  251, 265, 281, 296, 297, 298, 299, 306, 310, 329, 338, 372, 403]
    
    converted = []
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
        
        # HOTSPOT 드롭다운 파싱
        sentence, options, answer, explanation = parse_hotspot_dropdown(content, q_id)
        
        if not sentence:
            print(f"  ✗ 문장을 찾을 수 없음")
            failed.append(q_id)
            continue
        
        print(f"  문장: {sentence[:80]}...")
        print(f"  정답: {answer}")
        
        # JSON에서 해당 문제 찾아서 수정
        for q in data['questions']:
            if q['id'] == q_id:
                # 문장 끝에 빈칸 추가
                clean_sentence = sentence.strip()
                if not clean_sentence.endswith('_'):
                    # 마지막 마침표 제거하고 빈칸 추가
                    clean_sentence = clean_sentence.rstrip('.')
                    clean_sentence = clean_sentence + ' _______'
                
                q['question'] = clean_sentence
                q['questionType'] = 'MULTIPLE_CHOICE'
                q['options'] = options
                q['answer'] = answer
                
                # 해설이 있으면 업데이트
                if explanation:
                    q['explanation'] = explanation
                
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
    print(f"✓ 변환 완료: {len(converted)}개")
    if converted:
        print(f"   {converted}")
    
    if failed:
        print(f"\n✗ 변환 실패: {len(failed)}개")
        print(f"   {failed}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    convert_all_questions()

