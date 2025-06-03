#!/usr/bin/env python3
# cache_cleaner.py - 004 프로젝트 캐시 삭제 유틸리티

import os
import shutil
import glob
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class CacheCleaner:
    """캐시 삭제 및 정리 유틸리티"""
    
    def __init__(self, project_dir="."):
        self.project_dir = os.path.abspath(project_dir)
        self.deleted_files = []
        self.deleted_dirs = []
        self.total_size = 0
    
    def get_file_size(self, filepath):
        """파일 크기 반환 (바이트)"""
        try:
            return os.path.getsize(filepath)
        except (OSError, FileNotFoundError):
            return 0
    
    def format_size(self, size_bytes):
        """바이트를 읽기 쉬운 형태로 변환"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def clean_python_cache(self):
        """Python 바이트코드 캐시 삭제"""
        print("🐍 Python 캐시 파일 삭제 중...")
        
        # .pyc 파일 삭제
        pyc_pattern = os.path.join(self.project_dir, "**", "*.pyc")
        pyc_files = glob.glob(pyc_pattern, recursive=True)
        
        for file_path in pyc_files:
            try:
                size = self.get_file_size(file_path)
                os.remove(file_path)
                self.deleted_files.append(file_path)
                self.total_size += size
                print(f"   ✅ 삭제: {os.path.relpath(file_path)}")
            except Exception as e:
                print(f"   ❌ 실패: {os.path.relpath(file_path)} - {e}")
        
        # __pycache__ 디렉토리 삭제
        pycache_pattern = os.path.join(self.project_dir, "**", "__pycache__")
        pycache_dirs = glob.glob(pycache_pattern, recursive=True)
        
        for dir_path in pycache_dirs:
            try:
                # 디렉토리 크기 계산
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        self.total_size += self.get_file_size(os.path.join(root, file))
                
                shutil.rmtree(dir_path)
                self.deleted_dirs.append(dir_path)
                print(f"   ✅ 삭제: {os.path.relpath(dir_path)}/")
            except Exception as e:
                print(f"   ❌ 실패: {os.path.relpath(dir_path)} - {e}")
    
    def clean_log_files(self):
        """로그 파일 삭제"""
        print("📋 로그 파일 삭제 중...")
        
        log_patterns = [
            "*.log",
            "*.log.*",
            "logs/*",
            "log/*"
        ]
        
        for pattern in log_patterns:
            full_pattern = os.path.join(self.project_dir, pattern)
            log_files = glob.glob(full_pattern)
            
            for file_path in log_files:
                if os.path.isfile(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        os.remove(file_path)
                        self.deleted_files.append(file_path)
                        self.total_size += size
                        print(f"   ✅ 삭제: {os.path.relpath(file_path)}")
                    except Exception as e:
                        print(f"   ❌ 실패: {os.path.relpath(file_path)} - {e}")
    
    def clean_temp_files(self):
        """임시 파일 삭제"""
        print("🗂️ 임시 파일 삭제 중...")
        
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*.cache",
            "*.bak",
            "*.backup",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            "*.pid"
        ]
        
        for pattern in temp_patterns:
            full_pattern = os.path.join(self.project_dir, pattern)
            temp_files = glob.glob(full_pattern)
            
            for file_path in temp_files:
                if os.path.isfile(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        os.remove(file_path)
                        self.deleted_files.append(file_path)
                        self.total_size += size
                        print(f"   ✅ 삭제: {os.path.relpath(file_path)}")
                    except Exception as e:
                        print(f"   ❌ 실패: {os.path.relpath(file_path)} - {e}")
    
    def clean_pytest_cache(self):
        """pytest 캐시 삭제"""
        print("🧪 pytest 캐시 삭제 중...")
        
        pytest_dirs = [
            ".pytest_cache",
            ".cache",
            "test-results",
            ".coverage"
        ]
        
        for dir_name in pytest_dirs:
            dir_path = os.path.join(self.project_dir, dir_name)
            if os.path.exists(dir_path):
                try:
                    if os.path.isdir(dir_path):
                        # 디렉토리 크기 계산
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                self.total_size += self.get_file_size(os.path.join(root, file))
                        
                        shutil.rmtree(dir_path)
                        self.deleted_dirs.append(dir_path)
                        print(f"   ✅ 삭제: {dir_name}/")
                    else:
                        size = self.get_file_size(dir_path)
                        os.remove(dir_path)
                        self.deleted_files.append(dir_path)
                        self.total_size += size
                        print(f"   ✅ 삭제: {dir_name}")
                except Exception as e:
                    print(f"   ❌ 실패: {dir_name} - {e}")
    
    def clean_node_modules(self):
        """node_modules (만약 있다면) 삭제"""
        print("📦 Node.js 캐시 삭제 중...")
        
        node_dirs = [
            "node_modules",
            ".npm",
            "package-lock.json"
        ]
        
        for dir_name in node_dirs:
            dir_path = os.path.join(self.project_dir, dir_name)
            if os.path.exists(dir_path):
                try:
                    if os.path.isdir(dir_path):
                        # 큰 디렉토리는 크기 계산 생략
                        shutil.rmtree(dir_path)
                        self.deleted_dirs.append(dir_path)
                        print(f"   ✅ 삭제: {dir_name}/")
                    else:
                        size = self.get_file_size(dir_path)
                        os.remove(dir_path)
                        self.deleted_files.append(dir_path)
                        self.total_size += size
                        print(f"   ✅ 삭제: {dir_name}")
                except Exception as e:
                    print(f"   ❌ 실패: {dir_name} - {e}")
    
    def clean_git_cache(self):
        """Git 캐시 정리 (주의: .git은 건드리지 않음)"""
        print("🔄 Git 임시 파일 삭제 중...")
        
        git_temp_patterns = [
            ".git/index.lock",
            ".git/HEAD.lock",
            ".git/refs/heads/*.lock"
        ]
        
        for pattern in git_temp_patterns:
            full_pattern = os.path.join(self.project_dir, pattern)
            git_files = glob.glob(full_pattern)
            
            for file_path in git_files:
                if os.path.isfile(file_path):
                    try:
                        size = self.get_file_size(file_path)
                        os.remove(file_path)
                        self.deleted_files.append(file_path)
                        self.total_size += size
                        print(f"   ✅ 삭제: {os.path.relpath(file_path)}")
                    except Exception as e:
                        print(f"   ❌ 실패: {os.path.relpath(file_path)} - {e}")
    
    def scan_cache_files(self):
        """삭제할 캐시 파일들 미리 스캔"""
        print("🔍 캐시 파일 스캔 중...")
        
        cache_patterns = [
            "**/*.pyc",
            "**/__pycache__",
            "*.log",
            "*.tmp",
            "*.cache",
            ".pytest_cache",
            ".DS_Store"
        ]
        
        total_files = 0
        total_size = 0
        
        for pattern in cache_patterns:
            full_pattern = os.path.join(self.project_dir, pattern)
            files = glob.glob(full_pattern, recursive=True)
            
            for file_path in files:
                if os.path.exists(file_path):
                    total_files += 1
                    if os.path.isfile(file_path):
                        total_size += self.get_file_size(file_path)
                    elif os.path.isdir(file_path):
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                total_size += self.get_file_size(os.path.join(root, file))
        
        print(f"   📊 발견된 캐시 파일: {total_files}개")
        print(f"   💾 예상 삭제 용량: {self.format_size(total_size)}")
        
        return total_files, total_size
    
    def clean_all(self, confirm=True):
        """모든 캐시 삭제"""
        print("🧹 004 Google News 프로젝트 캐시 클리너")
        print("=" * 50)
        print(f"📁 프로젝트 경로: {self.project_dir}")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 사전 스캔
        total_files, estimated_size = self.scan_cache_files()
        
        if confirm and total_files > 0:
            response = input(f"\n❓ {total_files}개 파일 ({self.format_size(estimated_size)}) 삭제하시겠습니까? (y/N): ")
            if response.lower() not in ['y', 'yes', '예']:
                print("❌ 캐시 삭제 취소")
                return
        
        print("\n🚀 캐시 삭제 시작...")
        
        # 각종 캐시 삭제
        self.clean_python_cache()
        self.clean_log_files()
        self.clean_temp_files()
        self.clean_pytest_cache()
        self.clean_node_modules()
        self.clean_git_cache()
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("🎉 캐시 삭제 완료!")
        print(f"📄 삭제된 파일: {len(self.deleted_files)}개")
        print(f"📁 삭제된 디렉토리: {len(self.deleted_dirs)}개")
        print(f"💾 절약된 용량: {self.format_size(self.total_size)}")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.deleted_files or self.deleted_dirs:
            print("\n📋 삭제된 항목들:")
            for file_path in self.deleted_files[-10:]:  # 마지막 10개만 표시
                print(f"   • {os.path.relpath(file_path)}")
            if len(self.deleted_files) > 10:
                print(f"   ... 외 {len(self.deleted_files) - 10}개 파일")
            
            for dir_path in self.deleted_dirs:
                print(f"   • {os.path.relpath(dir_path)}/")

def main():
    """메인 실행 함수"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            # 스캔만 실행
            cleaner = CacheCleaner()
            cleaner.scan_cache_files()
        elif sys.argv[1] == "force":
            # 확인 없이 삭제
            cleaner = CacheCleaner()
            cleaner.clean_all(confirm=False)
        elif sys.argv[1] == "help":
            print("사용법:")
            print("  python3 cache_cleaner.py        # 대화형 캐시 삭제")
            print("  python3 cache_cleaner.py scan   # 캐시 파일만 스캔")
            print("  python3 cache_cleaner.py force  # 확인 없이 강제 삭제")
            print("  python3 cache_cleaner.py help   # 도움말")
        else:
            print("알 수 없는 옵션. 'help'를 참조하세요.")
    else:
        # 기본 실행 (대화형)
        cleaner = CacheCleaner()
        cleaner.clean_all(confirm=True)

if __name__ == "__main__":
    main()