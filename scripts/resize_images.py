"""
이미지 리사이징 및 최적화 스크립트
추출된 이미지를 웹에 최적화된 크기로 변환합니다.
"""

from PIL import Image
import os
from pathlib import Path

def resize_and_optimize_images(
    input_folder="images",
    output_folder="images",
    max_width=1200,
    quality=85
):
    """
    이미지를 리사이징하고 최적화합니다.
    
    Args:
        input_folder: 입력 이미지 폴더
        output_folder: 출력 이미지 폴더
        max_width: 최대 너비 (픽셀)
        quality: JPEG 품질 (1-100)
    """
    
    Path(output_folder).mkdir(exist_ok=True)
    
    supported_formats = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    processed_count = 0
    total_saved = 0
    
    print("=" * 60)
    print("이미지 최적화 시작")
    print("=" * 60)
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(supported_formats):
            continue
        
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        try:
            # 원본 파일 크기
            original_size = os.path.getsize(input_path)
            
            # 이미지 열기
            img = Image.open(input_path)
            
            # RGB로 변환 (PNG 투명도 제거)
            if img.mode in ('RGBA', 'LA', 'P'):
                # 투명 배경을 흰색으로
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 리사이징 (너비가 max_width보다 큰 경우만)
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
                print(f"\n📐 {filename}")
                print(f"   리사이징: {img.width}x{img.height} → {max_width}x{new_height}")
            else:
                print(f"\n✓ {filename}")
                print(f"   크기 유지: {img.width}x{img.height}")
            
            # 저장 (최적화)
            if filename.lower().endswith('.png'):
                img.save(output_path, 'PNG', optimize=True)
            else:
                img.save(output_path, 'JPEG', optimize=True, quality=quality)
            
            # 최적화된 파일 크기
            optimized_size = os.path.getsize(output_path)
            saved = original_size - optimized_size
            saved_percent = (saved / original_size * 100) if original_size > 0 else 0
            
            print(f"   원본: {original_size:,} bytes")
            print(f"   최적화: {optimized_size:,} bytes")
            print(f"   절약: {saved:,} bytes ({saved_percent:.1f}%)")
            
            processed_count += 1
            total_saved += saved
            
        except Exception as e:
            print(f"\n❌ 오류 - {filename}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"총 {processed_count}개 이미지 최적화 완료")
    print(f"총 절약된 용량: {total_saved:,} bytes ({total_saved/1024:.1f} KB)")
    print("=" * 60)


def create_thumbnail(
    input_folder="images",
    output_folder="images/thumbnails",
    max_size=(300, 300)
):
    """
    썸네일 이미지를 생성합니다.
    
    Args:
        input_folder: 입력 이미지 폴더
        output_folder: 썸네일 출력 폴더
        max_size: 썸네일 최대 크기 (width, height)
    """
    
    Path(output_folder).mkdir(exist_ok=True)
    
    supported_formats = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    count = 0
    
    print("\n썸네일 생성 중...")
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(supported_formats):
            continue
        
        input_path = os.path.join(input_folder, filename)
        
        # 파일명에 _thumb 추가
        name, ext = os.path.splitext(filename)
        thumb_filename = f"{name}_thumb{ext}"
        output_path = os.path.join(output_folder, thumb_filename)
        
        try:
            img = Image.open(input_path)
            img.thumbnail(max_size, Image.LANCZOS)
            img.save(output_path, optimize=True, quality=80)
            
            print(f"✓ {thumb_filename}")
            count += 1
            
        except Exception as e:
            print(f"❌ {filename}: {str(e)}")
    
    print(f"\n총 {count}개 썸네일 생성 완료")


if __name__ == "__main__":
    print("\n이미지 최적화 도구")
    print("1. 이미지 리사이징 및 최적화")
    print("2. 썸네일 생성")
    print("3. 둘 다 실행")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        resize_and_optimize_images()
    elif choice == "2":
        create_thumbnail()
    elif choice == "3":
        resize_and_optimize_images()
        create_thumbnail()
    else:
        print("잘못된 선택입니다.")

