"""
변환된 문제들의 선택지를 PDF에서 실제로 추출해서 업데이트
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

def extract_dropdown_options(content):
    """
    PDF 내용에서 드롭다운 선택지 추출
    Answer Area 섹션에서 선택지를 찾음
    """
    
    # Correct Answer 추출
    answer_match = re.search(r'Correct Answer:\s*([A-D])', content)
    answer_letter = answer_match.group(1) if answer_match else 'A'
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    # Answer Area 또는 Hot Area 다음에 나오는 선택지들 찾기
    options = []
    in_answer_area = False
    in_correct_answer = False
    
    for i, line in enumerate(lines):
        # Answer Area 시작
        if 'Answer Area' in line or 'Hot Area' in line:
            in_answer_area = True
            continue
        
        # Correct Answer 시작 - 여기서 중단
        if 'Correct Answer' in line:
            in_correct_answer = True
            break
        
        # Answer Area 내의 선택지 수집
        if in_answer_area:
            # 너무 짧거나 긴 줄은 제외
            if 10 < len(line) < 200:
                # URL, Reference 등 제외
                if not line.startswith('http') and \
                   not line.startswith('Reference') and \
                   not line.startswith('To complete') and \
                   not line.startswith('select the') and \
                   not line.startswith('HOTSPOT'):
                    # 이미 추가된 옵션이 아니면 추가
                    if line not in options:
                        options.append(line)
    
    # 최대 4개만 선택
    options = options[:4]
    
    # 옵션이 부족하면 Correct Answer 섹션 이후의 해설에서 추출 시도
    if len(options) < 4:
        explanation_start = False
        for line in lines:
            if 'Correct Answer' in line:
                explanation_start = True
                continue
            
            if explanation_start and not line.startswith('Reference') and not line.startswith('http'):
                if 10 < len(line) < 150 and line not in options:
                    options.append(line)
                    if len(options) >= 4:
                        break
    
    # 여전히 부족하면 기본값
    while len(options) < 4:
        options.append(f"Option {chr(65 + len(options))} (확인 필요)")
    
    # 정답 옵션이 첫 번째가 되도록 정렬 (선택적)
    # answer_index = ord(answer_letter) - 65
    # if 0 <= answer_index < len(options):
    #     correct_option = options.pop(answer_index)
    #     options.insert(0, correct_option)
    #     answer_letter = 'A'
    
    formatted_options = []
    for i, opt in enumerate(options):
        formatted_options.append({
            'letter': chr(65 + i),
            'text': opt
        })
    
    return formatted_options, answer_letter

def update_all_options():
    """모든 변환된 문제의 선택지 업데이트"""
    
    pdf_text = get_pdf_text()
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 변환된 문제들
    target_ids = [104, 115, 118, 126, 132, 212, 219, 230, 231, 232, 
                  251, 265, 296, 297, 298, 299, 306, 310, 329, 338, 372]
    
    updated = []
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
        
        # 선택지 추출
        options, answer = extract_dropdown_options(content)
        
        print(f"  선택지 {len(options)}개 추출:")
        for opt in options:
            print(f"    {opt['letter']}. {opt['text'][:60]}...")
        print(f"  정답: {answer}")
        
        # JSON에서 해당 문제 찾아서 업데이트
        for q in data['questions']:
            if q['id'] == q_id:
                q['options'] = options
                q['answer'] = answer
                
                updated.append(q_id)
                print(f"  ✓ 선택지 업데이트 완료")
                break
    
    # 저장
    with open('quiz_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"✓ 업데이트 완료: {len(updated)}개")
    
    if failed:
        print(f"\n✗ 실패: {len(failed)}개")
        print(f"   {failed}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    update_all_options()

