"""
퀴즈 앱 설정 및 이미지 검증 스크립트
모든 파일과 이미지가 올바르게 설정되었는지 확인합니다.
"""

import json
import os
from pathlib import Path

def check_dependencies():
    """필요한 Python 패키지 확인"""
    print("\n" + "=" * 60)
    print("1. Python 패키지 확인")
    print("=" * 60)
    
    required_packages = {
        'fitz': 'PyMuPDF',
        'PIL': 'Pillow'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} 설치됨")
        except ImportError:
            print(f"❌ {package} 미설치")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  설치 필요: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ 모든 필수 패키지 설치됨")
    return True


def check_files():
    """필수 파일 존재 확인"""
    print("\n" + "=" * 60)
    print("2. 필수 파일 확인")
    print("=" * 60)
    
    required_files = [
        'index.html',
        'app.js',
        'style.css',
        'quiz_data.json',
        'extract_images.py',
        'resize_images.py',
        'IMAGE_GUIDE.md',
        'WORKFLOW_GUIDE.md'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size:,} bytes)")
        else:
            print(f"❌ {filename} 없음")
            all_exist = False
    
    # 이미지 폴더 확인
    if os.path.exists('images'):
        image_count = len([f for f in os.listdir('images') 
                          if f.endswith(('.png', '.jpg', '.jpeg'))])
        print(f"✅ images/ 폴더 ({image_count}개 이미지)")
    else:
        print(f"⚠️  images/ 폴더 없음 (생성 필요)")
    
    return all_exist


def validate_json():
    """quiz_data.json 검증"""
    print("\n" + "=" * 60)
    print("3. quiz_data.json 검증")
    print("=" * 60)
    
    try:
        with open('quiz_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ JSON 파싱 성공")
        print(f"   제목: {data.get('title', 'N/A')}")
        print(f"   총 문제: {data.get('totalQuestions', 0)}개")
        print(f"   실제 문제: {len(data.get('questions', []))}개")
        
        # 불일치 확인
        if data.get('totalQuestions') != len(data.get('questions', [])):
            print(f"⚠️  문제 수 불일치 (메타데이터 업데이트 필요)")
        
        return data
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None


def check_images(data):
    """이미지 파일 확인"""
    print("\n" + "=" * 60)
    print("4. 이미지 파일 확인")
    print("=" * 60)
    
    if not data:
        print("⚠️  JSON 데이터 없음")
        return
    
    image_questions = []
    missing_images = []
    existing_images = []
    
    for q in data.get('questions', []):
        if 'image' in q and q['image']:
            image_questions.append(q)
            
            if os.path.exists(q['image']):
                size = os.path.getsize(q['image'])
                existing_images.append({
                    'id': q['id'],
                    'path': q['image'],
                    'size': size,
                    'type': q.get('questionType', 'UNKNOWN')
                })
            else:
                missing_images.append({
                    'id': q['id'],
                    'path': q['image']
                })
    
    print(f"📊 통계:")
    print(f"   이미지 문제: {len(image_questions)}개")
    print(f"   존재하는 이미지: {len(existing_images)}개")
    print(f"   누락된 이미지: {len(missing_images)}개")
    
    if existing_images:
        print(f"\n✅ 존재하는 이미지:")
        for img in existing_images[:5]:  # 처음 5개만 표시
            size_kb = img['size'] / 1024
            print(f"   Q{img['id']:3d} [{img['type']:10s}] {img['path']} ({size_kb:.1f} KB)")
        
        if len(existing_images) > 5:
            print(f"   ... 외 {len(existing_images) - 5}개")
        
        # 큰 파일 경고
        large_files = [img for img in existing_images if img['size'] > 500 * 1024]
        if large_files:
            print(f"\n⚠️  큰 파일 ({len(large_files)}개):")
            for img in large_files:
                size_mb = img['size'] / (1024 * 1024)
                print(f"   Q{img['id']} {img['path']} ({size_mb:.2f} MB)")
            print(f"   → resize_images.py 실행 권장")
    
    if missing_images:
        print(f"\n❌ 누락된 이미지:")
        for img in missing_images:
            print(f"   Q{img['id']:3d} {img['path']}")
    else:
        print(f"\n✅ 모든 이미지 파일 존재")
    
    # 문제 유형 통계
    type_stats = {}
    for q in image_questions:
        qtype = q.get('questionType', 'UNKNOWN')
        type_stats[qtype] = type_stats.get(qtype, 0) + 1
    
    if type_stats:
        print(f"\n📈 문제 유형별 분포:")
        for qtype, count in sorted(type_stats.items()):
            print(f"   {qtype:12s}: {count:3d}개")


def check_server():
    """서버 실행 여부 확인"""
    print("\n" + "=" * 60)
    print("5. 서버 확인")
    print("=" * 60)
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8080))
        sock.close()
        
        if result == 0:
            print("✅ 서버 실행 중 (http://127.0.0.1:8080)")
            print("   브라우저에서 접속 가능")
        else:
            print("❌ 서버 미실행")
            print("   실행 명령: npx http-server \"C:\\Users\\PC\\Desktop\\quiz-app\" -p 8080 -c-1")
    
    except Exception as e:
        print(f"⚠️  서버 확인 실패: {e}")


def generate_report():
    """종합 보고서 생성"""
    print("\n" + "=" * 60)
    print("검증 완료")
    print("=" * 60)
    
    print("\n다음 단계:")
    print("1. 서버가 실행 중이 아니면 시작:")
    print("   npx http-server \"C:\\Users\\PC\\Desktop\\quiz-app\" -p 8080 -c-1")
    print("\n2. 브라우저에서 접속:")
    print("   http://127.0.0.1:8080")
    print("\n3. 이미지 문제 추가:")
    print("   - WORKFLOW_GUIDE.md 참조")
    print("   - extract_images.py 실행")
    print("\n4. 문제 발생 시:")
    print("   - IMAGE_GUIDE.md의 트러블슈팅 섹션 확인")
    print("   - F12 → Console에서 오류 확인")


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 퀴즈 앱 설정 검증 도구")
    print("=" * 60)
    
    # 순차적 검증
    deps_ok = check_dependencies()
    files_ok = check_files()
    data = validate_json()
    check_images(data)
    check_server()
    
    generate_report()
    
    print("\n" + "=" * 60)
    print("검증 스크립트 실행 완료")
    print("=" * 60)

