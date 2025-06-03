#!/usr/bin/env python3
# notion_schema_checker.py - Notion 데이터베이스 스키마 확인 도구

import requests
import json
from config import Config

class NotionSchemaChecker:
    """Notion 데이터베이스 스키마 확인 및 분석"""
    
    def __init__(self):
        self.config = Config
        self.headers = {
            'Authorization': f'Bearer {Config.NOTION_API_KEY}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        self.base_url = "https://api.notion.com/v1"
        self.database_id = Config.NOTION_DATABASE_ID
    
    def check_database_schema(self):
        """데이터베이스 스키마 상세 확인"""
        print("🔍 Notion 데이터베이스 스키마 분석 중...")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/databases/{self.database_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                db_info = response.json()
                self._analyze_database_schema(db_info)
                return db_info
            else:
                print(f"❌ 데이터베이스 접근 실패: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 스키마 확인 오류: {e}")
            return None
    
    def _analyze_database_schema(self, db_info):
        """데이터베이스 스키마 분석"""
        # 데이터베이스 기본 정보
        title_info = db_info.get('title', [])
        db_title = "Unknown"
        if title_info and len(title_info) > 0:
            db_title = title_info[0].get('plain_text', 'Unknown')
        
        print(f"📊 데이터베이스 이름: {db_title}")
        print(f"🆔 데이터베이스 ID: {self.database_id}")
        print(f"📅 생성일: {db_info.get('created_time', 'Unknown')}")
        print(f"📝 수정일: {db_info.get('last_edited_time', 'Unknown')}")
        print()
        
        # 속성 분석
        properties = db_info.get('properties', {})
        print(f"🏗️ 데이터베이스 속성 ({len(properties)}개):")
        print("-" * 60)
        
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            prop_id = prop_info.get('id', 'unknown')
            
            print(f"📌 속성명: {prop_name}")
            print(f"   타입: {prop_type}")
            print(f"   ID: {prop_id}")
            
            # 타입별 상세 정보
            if prop_type == 'title':
                print(f"   📝 제목 속성 (메인 타이틀)")
            elif prop_type == 'select':
                options = prop_info.get('select', {}).get('options', [])
                option_names = [opt.get('name', '') for opt in options]
                print(f"   📋 선택 옵션: {', '.join(option_names)}")
            elif prop_type == 'multi_select':
                options = prop_info.get('multi_select', {}).get('options', [])
                option_names = [opt.get('name', '') for opt in options]
                print(f"   📋 다중선택 옵션: {', '.join(option_names)}")
            elif prop_type == 'number':
                number_format = prop_info.get('number', {}).get('format', 'number')
                print(f"   🔢 숫자 형식: {number_format}")
            elif prop_type == 'date':
                print(f"   📅 날짜 속성")
            elif prop_type == 'rich_text':
                print(f"   📝 서식있는 텍스트")
            elif prop_type == 'checkbox':
                print(f"   ☑️ 체크박스")
            
            print()
        
        # 권장 속성 매핑 제안
        print("💡 권장 속성 매핑:")
        print("-" * 60)
        self._suggest_property_mapping(properties)
    
    def _suggest_property_mapping(self, properties):
        """속성 매핑 제안"""
        # 제목 속성 찾기
        title_prop = None
        for name, info in properties.items():
            if info.get('type') == 'title':
                title_prop = name
                break
        
        if title_prop:
            print(f"✅ 제목 속성: '{title_prop}' 사용 권장")
        else:
            print("❌ 제목 속성을 찾을 수 없습니다!")
        
        # 다른 속성들 매핑 제안
        mapping_suggestions = {}
        
        for name, info in properties.items():
            prop_type = info.get('type')
            
            if prop_type == 'date' and 'date' in name.lower():
                mapping_suggestions['날짜'] = name
            elif prop_type == 'select' and 'category' in name.lower():
                mapping_suggestions['카테고리'] = name
            elif prop_type == 'number' and 'count' in name.lower():
                mapping_suggestions['기사 수'] = name
            elif prop_type == 'rich_text' and 'keyword' in name.lower():
                mapping_suggestions['키워드'] = name
            elif prop_type == 'select' and 'status' in name.lower():
                mapping_suggestions['상태'] = name
        
        for purpose, prop_name in mapping_suggestions.items():
            print(f"✅ {purpose}: '{prop_name}' 사용 권장")
        
        return title_prop, mapping_suggestions
    
    def generate_compatible_properties(self):
        """호환 가능한 속성 딕셔너리 생성"""
        print("\n🔧 호환 가능한 속성 코드 생성 중...")
        
        db_info = self.check_database_schema()
        if not db_info:
            return None
        
        properties = db_info.get('properties', {})
        title_prop, mappings = self._suggest_property_mapping(properties)
        
        if not title_prop:
            print("❌ 제목 속성이 없어서 코드 생성 불가능")
            return None
        
        # 코드 생성
        print("\n📝 생성된 속성 매핑 코드:")
        print("=" * 60)
        
        code = f'''
def _build_page_properties(self, today, current_time, articles, keywords, summary):
    """실제 데이터베이스 스키마에 맞는 페이지 속성 구성"""
    try:
        title = f"🤖 Google News AI 리포트 - {{today}} {{current_time}}"
        
        properties = {{
            "{title_prop}": {{  # 실제 제목 속성명 사용
                "title": [
                    {{
                        "type": "text",
                        "text": {{"content": title}}
                    }}
                ]
            }}'''
        
        # 다른 속성들 추가
        for purpose, prop_name in mappings.items():
            prop_info = properties.get(prop_name, {})
            prop_type = prop_info.get('type')
            
            if prop_type == 'date' and '날짜' in purpose:
                code += f'''
            "{prop_name}": {{
                "date": {{"start": today}}
            }},'''
            elif prop_type == 'select' and '카테고리' in purpose:
                code += f'''
            "{prop_name}": {{
                "select": {{"name": "AI 뉴스"}}
            }},'''
            elif prop_type == 'number' and '기사' in purpose:
                code += f'''
            "{prop_name}": {{
                "number": len(articles)
            }},'''
            elif prop_type == 'rich_text' and '키워드' in purpose:
                code += f'''
            "{prop_name}": {{
                "rich_text": [
                    {{
                        "type": "text",
                        "text": {{"content": ", ".join(keywords[:10]) if keywords else "AI, Google News"}}
                    }}
                ]
            }},'''
            elif prop_type == 'select' and '상태' in purpose:
                code += f'''
            "{prop_name}": {{
                "select": {{"name": "완료"}}
            }},'''
        
        code += '''
        }
        
        return properties
        
    except Exception as e:
        logger.error(f"페이지 속성 구성 오류: {e}")
        # 최소한의 속성만 반환
        return {
            "''' + title_prop + '''": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": f"Google News AI 리포트 - {today}"}
                    }
                ]
            }
        }
'''
        
        print(code)
        
        # 파일로 저장
        with open('notion_properties_fix.py', 'w', encoding='utf-8') as f:
            f.write(code)
        
        print("\n✅ notion_properties_fix.py 파일로 저장 완료")
        print("이 코드를 notion_saver.py의 _build_page_properties 메서드에 적용하세요!")
        
        return code

def main():
    """메인 실행"""
    checker = NotionSchemaChecker()
    
    print("🔍 Notion 데이터베이스 스키마 확인 도구")
    print("=" * 60)
    
    # 스키마 확인
    checker.check_database_schema()
    
    # 호환 코드 생성
    checker.generate_compatible_properties()

if __name__ == "__main__":
    main()
