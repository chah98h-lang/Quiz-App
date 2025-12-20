"""
HOTSPOT 문제 개선 - 해설에서 statements 추출
"""

import fitz
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EXCLUDE_IDS = [97, 109, 112, 168, 199, 215, 276, 328]

def extract_statements_from_explanation(content):
    """
    해설(Box 1, Box 2, Box 3)에서 statement 내용 유추
    
    예: Box 1: Yes - Explanation about statement 1
    """
    statements = []
    answers = []
    
    # Box 패턴 찾기
    box_pattern = r'Box (\d+):\s*(Yes|No)\s*-\s*(.+?)(?=Box \d+:|References?:|Topic|$)'
    matches = re.findall(box_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for box_num, answer, explanation in matches:
        # 해설의 첫 문장을 statement로 사용
        # 또는 해설에서 키워드 추출
        explanation = explanation.strip()
        
        # 첫 문장만 추출 (마침표까지)
        first_sentence = re.split(r'[.!?]\s+', explanation)[0]
        if first_sentence:
            first_sentence = first_sentence[:200]  # 최대 200자
        else:
            first_sentence = explanation[:200]
        
        statements.append(first_sentence)
        answers.append(answer.capitalize())
    
    return statements, answers

def extract_dropdown_options(content):
    """
    Dropdown 문제의 선택지 추출
    해설이나 Correct Answer에서 추출
    """
    
    # 선택지 패턴 찾기 시도
    # 예: "in a private cloud", "in a hybrid cloud", "in the public cloud"
    
    # Correct Answer 찾기
    answer_match = re.search(r'Correct Answer:\s*(.+?)(?=\n\n|References?:|Topic|$)', content, re.DOTALL)
    if not answer_match:
        return None, None
    
    answer_section = answer_match.group(1)
    
    # 답 추출
    answer_letter = answer_section[0] if answer_section else 'A'
    
    # 해설에서 옵션들 찾기
    # 일반적인 패턴들
    options_patterns = [
        r'(in (?:a|the) (?:private|public|hybrid) cloud)',
        r'(on (?:a|the) .+? host)',
        r'(Software|Platform|Infrastructure) as a Service',
    ]
    
    found_options = set()
    for pattern in options_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            found_options.add(match)
    
    if found_options:
        options = []
        for i, opt_text in enumerate(sorted(found_options)):
            options.append({
                'letter': chr(65 + i),  # A, B, C, D
                'text': opt_text
            })
        return options[:4], answer_letter  # 최대 4개
    
    return None, answer_letter

def improve_single_question(q_id, content):
    """단일 문제 개선"""
    
    content_upper = content.upper()
    
    # Checkbox 형식
    if any(kw in content_upper for kw in ['BOX 1:', 'BOX 2:', 'BOX 3:']):
        if 'SELECT YES IF' in content_upper or 'SELECT NO IF' in content_upper:
            statements, answers = extract_statements_from_explanation(content)
            
            if statements and len(statements) == len(answers):
                # 해설 전체
                explanation = ""
                exp_match = re.search(r'(Box 1:.+?)(?=References?:|Topic|$)', content, re.DOTALL | re.IGNORECASE)
                if exp_match:
                    explanation = exp_match.group(1).strip()[:1000]
                
                return {
                    'questionType': 'HOTSPOT',
                    'question': 'For each of the following statements, select Yes if the statement is true. Otherwise, select No.\nNOTE: Each correct selection is worth one point.',
                    'statements': statements,
                    'answer': answers,
                    'explanation': explanation
                }
    
    # Dropdown 형식
    if 'TO COMPLETE THE SENTENCE' in content_upper or 'SELECT THE APPROPRIATE OPTION' in content_upper:
        options, answer = extract_dropdown_options(content)
        
        if options:
            # 문장 패턴 찾기
            sentence_pattern = r'(An? .+?_+.+?\.)'
            sentence_match = re.search(sentence_pattern, content)
            
            question = sentence_match.group(1) if sentence_match else "To complete the sentence, select the appropriate option in the answer area."
            
            # 해설
            exp_match = re.search(r'Correct Answer:(.+?)(?=References?:|Topic|$)', content, re.DOTALL)
            explanation = exp_match.group(1).strip()[:1000] if exp_match else ""
            
            return {
                'questionType': 'MULTIPLE_CHOICE',
                'question': question,
                'options': options,
                'answer': answer,
                'explanation': explanation
            }
    
    return None

def improve_all_questions(pdf_path, json_path):
    """모든 HOTSPOT 문제 개선"""
    
    print("PDF 로딩 중...")
    pdf = fitz.open(pdf_path)
    pdf_text = ""
    for page in pdf:
        pdf_text += page.get_text() + "\n"
    pdf.close()
    
    print("JSON 로딩 중...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 개선 대상 찾기
    targets = []
    for q in data['questions']:
        if q['id'] in EXCLUDE_IDS:
            continue
        
        if q.get('questionType') in ['HOTSPOT', 'HOT_AREA']:
            # statements가 placeholder인 경우
            if 'statements' in q:
                if any('이미지로 되어 있어' in str(s) for s in q.get('statements', [])):
                    targets.append(q)
            # options가 placeholder인 경우
            elif 'options' in q:
                if any('PDF 참조' in str(opt.get('text', '')) for opt in q.get('options', [])):
                    targets.append(q)
    
    print(f"개선 대상: {len(targets)}개")
    
    improved_count = 0
    
    for q in targets:
        q_num = q['id']
        
        # PDF에서 추출
        pattern = rf'Question #{q_num}\n(.+?)Question #{q_num + 1}'
        match = re.search(pattern, pdf_text, re.DOTALL)
        
        if not match:
            pattern = rf'Question #{q_num}\n(.+?)$'
            match = re.search(pattern, pdf_text, re.DOTALL)
        
        if not match:
            print(f"Q{q_num}: PDF에서 찾을 수 없음")
            continue
        
        content = match.group(1)
        
        # 개선
        improved = improve_single_question(q_num, content)
        
        if improved:
            q.update(improved)
            improved_count += 1
            print(f"Q{q_num}: 개선 완료")
        else:
            print(f"Q{q_num}: 개선 실패")
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {improved_count}개 문제 개선 완료!")

if __name__ == "__main__":
    improve_all_questions("AZ-900 영문 474.pdf", "quiz_data.json")

