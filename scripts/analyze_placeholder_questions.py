"""
Placeholder 문제들의 빈칸 위치 분석
"""

import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_blank_position(question_text):
    """
    빈칸 위치 분석
    Returns: 'front', 'back', 'middle', or 'none'
    """
    
    # 빈칸 패턴
    blank_patterns = [
        r'^_{3,}',  # 시작에 빈칸
        r'_{3,}$',  # 끝에 빈칸  
        r'_{3,}',   # 빈칸 있음
    ]
    
    # 빈칸이 처음에 있는지
    if re.search(r'^_{3,}', question_text.strip()):
        return 'front'
    
    # 빈칸이 끝에 있는지
    if re.search(r'_{3,}\s*\.?\s*$', question_text.strip()):
        return 'back'
    
    # 빈칸이 중간에 있는지
    if re.search(r'_{3,}', question_text):
        return 'middle'
    
    # 빈칸이 없는 경우, 문장 구조로 판단
    # "... to" 등으로 끝나면 뒤에 올 가능성
    back_indicators = [
        r'\s+to\s*\.?\s*$',
        r'\s+can\s*\.?\s*$',
        r'\s+should\s*\.?\s*$',
        r'\s+will\s*\.?\s*$',
        r'\s+must\s*\.?\s*$',
    ]
    
    for pattern in back_indicators:
        if re.search(pattern, question_text.strip()):
            return 'back'
    
    return 'none'

def main():
    """메인 함수"""
    
    print("JSON 로딩 중...")
    with open('quiz_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_ids = [104, 115, 118, 126, 132, 188, 212, 219, 230, 231, 232, 
                  251, 265, 281, 296, 297, 298, 299, 306, 310, 329, 338, 372, 403]
    
    front_questions = []
    back_questions = []
    middle_questions = []
    none_questions = []
    
    for q_id in target_ids:
        # JSON에서 해당 문제 찾기
        question = None
        for q in data['questions']:
            if q['id'] == q_id:
                question = q
                break
        
        if not question:
            print(f"Q{q_id}: 찾을 수 없음")
            continue
        
        question_text = question.get('question', '')
        position = analyze_blank_position(question_text)
        
        print(f"\nQ{q_id}:")
        print(f"  문장: {question_text[:100]}...")
        print(f"  빈칸 위치: {position}")
        
        if position == 'front':
            front_questions.append(q_id)
        elif position == 'back':
            back_questions.append(q_id)
        elif position == 'middle':
            middle_questions.append(q_id)
        else:
            none_questions.append(q_id)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"✓ 빈칸이 앞에 있는 문제: {len(front_questions)}개")
    if front_questions:
        print(f"   {front_questions}")
    
    print(f"\n✓ 빈칸이 뒤에 있는 문제: {len(back_questions)}개")
    if back_questions:
        print(f"   {back_questions}")
    
    print(f"\n⚠ 빈칸이 중간에 있는 문제: {len(middle_questions)}개")
    if middle_questions:
        print(f"   {middle_questions}")
    
    print(f"\n? 빈칸이 없거나 불명확한 문제: {len(none_questions)}개")
    if none_questions:
        print(f"   {none_questions}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()

