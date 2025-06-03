#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텔레그램 봇 연결 테스트 도구
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_telegram_bot():
    """텔레그램 봇 연결 테스트"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print("🤖 텔레그램 봇 연결 테스트")
    print("=" * 40)
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID가 설정되지 않았습니다")
        return False
    
    print(f"🔑 Bot Token: {bot_token[:10]}...")
    print(f"💬 Chat ID: {chat_id}")
    
    # 1. 봇 정보 확인
    print("\n1. 봇 정보 확인...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info['result']
                print(f"✅ 봇 이름: {bot_data.get('first_name', 'Unknown')}")
                print(f"✅ 봇 사용자명: @{bot_data.get('username', 'Unknown')}")
            else:
                print(f"❌ 봇 정보 오류: {bot_info.get('description', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 봇 정보 확인 실패: {e}")
        return False
    
    # 2. 간단한 메시지 전송 테스트
    print("\n2. 메시지 전송 테스트...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # 간단한 텍스트 메시지
        simple_message = "🧪 Google News AI 시스템 테스트 메시지입니다."
        
        data = {
            'chat_id': chat_id,
            'text': simple_message,
            'parse_mode': 'HTML'  # Markdown 대신 HTML 사용
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ 메시지 전송 성공!")
                print(f"📱 메시지 ID: {result['result']['message_id']}")
                return True
            else:
                print(f"❌ 메시지 전송 실패: {result.get('description', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 메시지 전송 실패: {e}")
        return False

def get_chat_id_info(bot_token):
    """채팅 ID 정보 확인"""
    print("\n📋 최근 메시지에서 Chat ID 찾기...")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok') and result.get('result'):
                updates = result['result']
                print(f"📨 최근 {len(updates)}개 업데이트 발견:")
                
                for update in updates[-5:]:  # 최근 5개만
                    if 'message' in update:
                        msg = update['message']
                        chat = msg.get('chat', {})
                        user = msg.get('from', {})
                        
                        chat_id = chat.get('id')
                        chat_type = chat.get('type', 'unknown')
                        username = user.get('username', 'no_username')
                        first_name = user.get('first_name', 'Unknown')
                        
                        print(f"  💬 Chat ID: {chat_id}")
                        print(f"     유형: {chat_type}")
                        print(f"     사용자: {first_name} (@{username})")
                        print(f"     메시지: {msg.get('text', '')[:30]}...")
                        print()
            else:
                print("📭 최근 메시지가 없습니다")
                print("💡 봇에게 /start 메시지를 보내보세요")
        else:
            print(f"❌ 업데이트 확인 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Chat ID 정보 확인 실패: {e}")

def main():
    """메인 실행"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "chatid":
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if bot_token:
            get_chat_id_info(bot_token)
        else:
            print("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다")
        return
    
    success = test_telegram_bot()
    
    if success:
        print("\n🎉 텔레그램 봇 연결 성공!")
        print("💡 이제 메인 시스템을 실행할 수 있습니다")
    else:
        print("\n❌ 텔레그램 봇 연결 실패")
        print("\n🔧 해결 방법:")
        print("1. .env 파일의 TELEGRAM_BOT_TOKEN 확인")
        print("2. .env 파일의 TELEGRAM_CHAT_ID 확인") 
        print("3. 봇이 채팅방에 추가되어 있는지 확인")
        print("4. python3 telegram_test.py chatid 로 Chat ID 확인")

if __name__ == "__main__":
    main()
