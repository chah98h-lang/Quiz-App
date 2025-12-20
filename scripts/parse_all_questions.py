"""
AZ-900 PDF에서 474개 문항 전체 추출 스크립트
텍스트 문제 + 이미지 문제 모두 파싱
"""

import fitz  # PyMuPDF
import json
import re
import os
from pathlib import Path

def extract_all_questions_from_pdf(pdf_path, output_json="quiz_data_full.json", image_folder="images"):
    """PDF에서 모든 문제 추출 (텍스트 + 이미지)"""
    
    # 이미지 폴더 생성
    Path(image_folder).mkdir(exist_ok=True)
    
    # PDF 열기
    pdf = fitz.open(pdf_path)
    
    questions = []
    current_question = None
    question_counter = 1
    
    print(f"PDF 총 페이지 수: {pdf.page_count}")
    print("=" * 60)
    
    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        text = page.get_text()
        
        # 페이지에 이미지가 있는지 확인
        images = page.get_images()
        has_images = len(images) > 0
        
        # DRAG DROP, Hot Area, Hotspot 키워드 확인
        is_image_question = any(keyword in text.upper() for keyword in 
                               ["DRAG DROP", "HOT AREA", "HOTSPOT", "HOT SPOT"])
        
        # 문제 번호 패턴 찾기 (Question 1, Q1, QUESTION 1 등)
        question_pattern = r'(?:QUESTION|Question|Q\.?)\s*(\d+)'
        matches = re.findall(question_pattern, text)
        
        if matches:
            # 새로운 문제 시작
            if current_question:
                questions.append(current_question)
            
            q_num = matches[0]
            
            current_question = {
                "id": question_counter,
                "original_number": q_num,
                "page": page_num + 1,
                "question": "",
                "questionType": "IMAGE" if is_image_question else "TEXT",
                "options": [],
                "answer": "",
                "explanation": "",
                "hasImage": has_images
            }
            
            # 이미지가 있으면 추출
            if has_images and is_image_question:
                for img_index, img in enumerate(images):
                    try:
                        xref = img[0]
                        base_image = pdf.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        image_filename = f"q{question_counter}_page{page_num + 1:03d}_img{img_index + 1}.{image_ext}"
                        image_path = os.path.join(image_folder, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        current_question["image"] = f"{image_folder}/{image_filename}"
                        print(f"[OK] Q{question_counter} - 이미지 추출: {image_filename}")
                    except:
                        pass
            
            # 텍스트 파싱 (간단한 버전)
            lines = text.split('\n')
            
            # 문제 텍스트 추출 (Question X 다음 라인부터)
            question_text = []
            options = []
            answer_text = ""
            explanation_text = ""
            
            in_question = False
            in_options = False
            in_answer = False
            in_explanation = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Question 라인 이후 시작
                if re.match(question_pattern, line):
                    in_question = True
                    continue
                
                # Answer: 섹션
                if line.startswith('Answer:') or line.startswith('Correct Answer:'):
                    in_answer = True
                    in_options = False
                    answer_text = line.replace('Answer:', '').replace('Correct Answer:', '').strip()
                    continue
                
                # Explanation 섹션
                if 'Explanation:' in line or 'Reference:' in line:
                    in_explanation = True
                    in_answer = False
                    explanation_text = line.replace('Explanation:', '').replace('Reference:', '').strip()
                    continue
                
                # 선택지 (A. B. C. D.)
                if re.match(r'^[A-Z]\.\s', line):
                    in_options = True
                    in_question = False
                    options.append(line)
                    continue
                
                # 텍스트 수집
                if in_question and not in_options:
                    question_text.append(line)
                elif in_options and not in_answer:
                    if options:
                        options[-1] += ' ' + line
                elif in_explanation:
                    explanation_text += ' ' + line
            
            # 문제 정보 저장
            if question_text:
                current_question["question"] = ' '.join(question_text)
            
            # 선택지 파싱
            for opt in options:
                match = re.match(r'^([A-Z])\.\s*(.+)', opt)
                if match:
                    current_question["options"].append({
                        "letter": match.group(1),
                        "text": match.group(2).strip()
                    })
            
            if answer_text:
                current_question["answer"] = answer_text
            
            if explanation_text:
                current_question["explanation"] = explanation_text
            
            question_counter += 1
            
            # 진행 상황 표시
            if question_counter % 10 == 0:
                print(f"진행 중... {question_counter}개 문제 처리")
    
    # 마지막 문제 추가
    if current_question:
        questions.append(current_question)
    
    pdf.close()
    
    # JSON 생성
    quiz_data = {
        "title": "AZ-900 Azure Fundamentals - Full",
        "description": f"Microsoft Azure Fundamentals - {len(questions)} Questions",
        "totalQuestions": len(questions),
        "questions": questions
    }
    
    # JSON 파일 저장
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"[완료] 총 {len(questions)}개 문제 추출!")
    print(f"[파일] {output_json}")
    print(f"[이미지] {image_folder}/ 폴더")
    
    # 통계
    text_questions = sum(1 for q in questions if q.get("questionType") == "TEXT")
    image_questions = sum(1 for q in questions if q.get("questionType") == "IMAGE")
    
    print(f"\n[통계]")
    print(f"   텍스트 문제: {text_questions}개")
    print(f"   이미지 문제: {image_questions}개")
    
    return quiz_data


if __name__ == "__main__":
    import sys
    import io
    
    # UTF-8 출력 설정
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("AZ-900 PDF 전체 문항 추출 시작")
    print("=" * 60)
    
    pdf_file = "AZ-900 영문 474.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"[오류] '{pdf_file}' 파일을 찾을 수 없습니다.")
        print("현재 디렉토리의 PDF 파일명을 확인해주세요.")
    else:
        print(f"[PDF] {pdf_file}")
        print("추출 시작...\n")
        
        result = extract_all_questions_from_pdf(pdf_file)
        
        print("\n[완료!]")
        print("\n다음 단계:")
        print("1. quiz_data_full.json 파일 확인")
        print("2. 기존 quiz_data.json 백업")
        print("3. quiz_data_full.json -> quiz_data.json으로 교체")
        print("4. 서버 재시작")

