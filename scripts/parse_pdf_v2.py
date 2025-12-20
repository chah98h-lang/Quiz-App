"""
AZ-900 PDF 파싱 스크립트 v2
실제 PDF 구조에 맞게 수정
"""

import fitz
import json
import re
import os
import sys
import io
from pathlib import Path

# UTF-8 출력
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_az900_pdf(pdf_path, output_json="quiz_data_full.json", image_folder="images"):
    """AZ-900 PDF 파싱"""
    
    Path(image_folder).mkdir(exist_ok=True)
    
    pdf = fitz.open(pdf_path)
    all_text = ""
    
    print(f"PDF 총 페이지: {pdf.page_count}")
    print("텍스트 추출 중...")
    
    # 모든 텍스트 추출
    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        all_text += page.get_text() + "\n"
        
        if (page_num + 1) % 50 == 0:
            print(f"  {page_num + 1} 페이지 처리...")
    
    print("문제 파싱 중...")
    
    # Question #X 패턴으로 문제 분리
    question_pattern = r'Question #(\d+)'
    questions_raw = re.split(question_pattern, all_text)
    
    questions = []
    
    # questions_raw는 [시작텍스트, 번호1, 내용1, 번호2, 내용2, ...] 형태
    for i in range(1, len(questions_raw), 2):
        if i + 1 >= len(questions_raw):
            break
            
        question_num = questions_raw[i]
        question_content = questions_raw[i + 1]
        
        # 문제 파싱
        q_data = parse_single_question(question_num, question_content, pdf, image_folder)
        
        if q_data:
            questions.append(q_data)
            
            if len(questions) % 10 == 0:
                print(f"  {len(questions)}개 문제 처리...")
    
    pdf.close()
    
    # JSON 생성
    quiz_data = {
        "title": "AZ-900 Azure Fundamentals",
        "description": f"Microsoft Azure Fundamentals - {len(questions)} Questions",
        "totalQuestions": len(questions),
        "questions": questions
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"[완료] {len(questions)}개 문제 추출!")
    print(f"[저장] {output_json}")
    
    # 통계
    text_q = sum(1 for q in questions if not q.get('image'))
    image_q = sum(1 for q in questions if q.get('image'))
    
    print(f"\n[통계]")
    print(f"  텍스트 문제: {text_q}개")
    print(f"  이미지 문제: {image_q}개")
    
    return quiz_data


def parse_single_question(question_num, content, pdf, image_folder):
    """개별 문제 파싱"""
    
    lines = content.strip().split('\n')
    
    # 기본 데이터
    q_data = {
        "id": int(question_num),
        "original_number": question_num,
        "question": "",
        "options": [],
        "answer": "",
        "explanation": ""
    }
    
    # DRAG DROP, Hot Area 등 확인
    content_upper = content.upper()
    if 'DRAG DROP' in content_upper:
        q_data["questionType"] = "DRAG_DROP"
    elif 'HOT AREA' in content_upper or 'HOTAREA' in content_upper:
        q_data["questionType"] = "HOT_AREA"
    elif 'HOTSPOT' in content_upper or 'HOT SPOT' in content_upper:
        q_data["questionType"] = "HOTSPOT"
    else:
        q_data["questionType"] = "MULTIPLE_CHOICE"
    
    # 정답 추출 (Correct Answer: X)
    answer_match = re.search(r'Correct Answer:\s*([A-Z,\s]+)', content)
    if answer_match:
        q_data["answer"] = answer_match.group(1).strip()
    
    # References/Explanation 추출
    ref_match = re.search(r'(?:References?|Explanation):\s*(.+?)(?=Community vote|Topic|Question|$)', content, re.DOTALL | re.IGNORECASE)
    if ref_match:
        q_data["explanation"] = ref_match.group(1).strip()[:500]  # 최대 500자
    
    # 질문 텍스트 추출
    # Correct Answer 이전까지가 질문 + 선택지
    answer_pos = content.find('Correct Answer:')
    if answer_pos > 0:
        question_part = content[:answer_pos]
    else:
        question_part = content
    
    # 선택지 추출 (A. B. C. D.)
    options_pattern = r'^([A-Z])\.\s*(.+?)(?=^[A-Z]\.|Correct Answer:|$)'
    option_matches = re.findall(options_pattern, question_part, re.MULTILINE | re.DOTALL)
    
    for letter, text in option_matches:
        q_data["options"].append({
            "letter": letter,
            "text": text.strip()[:200]  # 최대 200자
        })
    
    # 질문 텍스트 (선택지 이전까지)
    if option_matches:
        first_option_pos = question_part.find(f"{option_matches[0][0]}.")
        question_text = question_part[:first_option_pos] if first_option_pos > 0 else question_part
    else:
        question_text = question_part
    
    # 불필요한 부분 제거
    question_text = re.sub(r'DRAG DROP\s*-?\s*', '', question_text, flags=re.IGNORECASE)
    question_text = re.sub(r'Select and Place:\s*', '', question_text, flags=re.IGNORECASE)
    question_text = re.sub(r'HOT AREA\s*-?\s*', '', question_text, flags=re.IGNORECASE)
    question_text = question_text.strip()
    
    q_data["question"] = question_text[:1000]  # 최대 1000자
    
    return q_data


if __name__ == "__main__":
    print("=" * 60)
    print("AZ-900 PDF 파싱 시작")
    print("=" * 60)
    
    pdf_file = "AZ-900 영문 474.pdf"
    
    if os.path.exists(pdf_file):
        result = parse_az900_pdf(pdf_file)
        print("\n완료!")
    else:
        print(f"[오류] {pdf_file} 파일을 찾을 수 없습니다.")

