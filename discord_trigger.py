#!/usr/bin/env python3
# discord_trigger.py - 디스코드 메시지로 Google News AI 시스템 트리거

import discord
import asyncio
import subprocess
import sys
import os
import logging
from datetime import datetime
from config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_trigger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiscordTrigger:
    """디스코드 메시지 기반 Google News AI 트리거 시스템"""
    
    def __init__(self):
        self.config = Config
        
        # Discord 설정
        self.bot_token = os.getenv('DISCORD_BOT_TOKEN')
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID')) if os.getenv('DISCORD_CHANNEL_ID') else None
        
        # 트리거 키워드들
        self.trigger_keywords = [
            '!뉴스',
            '!news', 
            '!ai뉴스',
            '!google뉴스',
            '!실행',
            '!run',
            'google news',
            'ai 뉴스 수집',
            '뉴스 업데이트'
        ]
        
        # 관리자 사용자 ID들 (옵션)
        self.admin_users = []  # 필요시 Discord 사용자 ID 추가
        
        # Discord 클라이언트 설정
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        # 실행 상태 관리
        self.is_running = False
        self.last_execution = None
        
        # 이벤트 핸들러 등록
        self._setup_events()
    
    def _setup_events(self):
        """Discord 이벤트 핸들러 설정"""
        
        @self.client.event
        async def on_ready():
            logger.info(f'✅ Discord 봇 로그인 성공: {self.client.user}')
            
            if self.channel_id:
                channel = self.client.get_channel(self.channel_id)
                if channel:
                    logger.info(f'📡 모니터링 채널: #{channel.name} ({self.channel_id})')
                    
                    # 봇 시작 알림 (옵션)
                    startup_message = f"""🤖 **Google News AI 봇이 시작되었습니다!**

⚡ **트리거 명령어:**
• `!뉴스` - AI 뉴스 수집 실행
• `!news` - AI 뉴스 수집 실행  
• `!상태` - 봇 상태 확인
• `!도움` - 명령어 도움말

🕐 **마지막 실행:** {self.last_execution or '없음'}
📍 **현재 상태:** 대기 중

메시지를 입력하면 Google News에서 최신 AI 뉴스를 수집합니다! 🚀"""
                    
                    await channel.send(startup_message)
                else:
                    logger.error(f'❌ 채널 ID {self.channel_id}를 찾을 수 없습니다')
            else:
                logger.warning('⚠️ DISCORD_CHANNEL_ID가 설정되지 않았습니다')
        
        @self.client.event
        async def on_message(message):
            # 봇 자신의 메시지는 무시
            if message.author == self.client.user:
                return
            
            # 지정된 채널에서만 동작 (설정된 경우)
            if self.channel_id and message.channel.id != self.channel_id:
                return
            
            await self._handle_message(message)
    
    async def _handle_message(self, message):
        """메시지 처리"""
        content = message.content.lower().strip()
        author = message.author
        
        logger.info(f"📨 메시지 수신: '{content}' from {author.name}")
        
        try:
            # 상태 확인 명령
            if content in ['!상태', '!status', '!info']:
                await self._send_status(message)
                return
            
            # 도움말 명령
            if content in ['!도움', '!help', '!명령어']:
                await self._send_help(message)
                return
            
            # 트리거 키워드 확인
            triggered = False
            for keyword in self.trigger_keywords:
                if keyword in content:
                    triggered = True
                    break
            
            if triggered:
                if self.is_running:
                    await message.add_reaction('⏳')
                    await message.reply("🔄 현재 AI 뉴스 수집이 진행 중입니다. 잠시만 기다려주세요!")
                    return
                
                # 실행 트리거
                await self._trigger_news_collection(message)
            else:
                # 트리거 키워드가 없지만 AI나 뉴스 관련 언급이 있으면 힌트 제공
                if any(word in content for word in ['ai', '뉴스', 'news', '인공지능', '기사', '정보']):
                    await message.add_reaction('💡')
                    hint_msg = await message.reply("💡 AI 뉴스 수집을 원하시면 `!뉴스` 또는 `!news`를 입력해주세요!")
                    
                    # 5초 후 힌트 메시지 삭제
                    await asyncio.sleep(5)
                    try:
                        await hint_msg.delete()
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ 메시지 처리 중 오류: {e}")
            await message.add_reaction('❌')
            await message.reply(f"❌ 메시지 처리 중 오류가 발생했습니다: {str(e)}")
    
    async def _trigger_news_collection(self, message):
        """AI 뉴스 수집 트리거"""
        try:
            # 실행 상태 설정
            self.is_running = True
            
            # 즉시 반응 및 알림
            await message.add_reaction('🚀')
            status_msg = await message.reply("🚀 Google News AI 뉴스 수집을 시작합니다! 약 1-2분 소요될 예정입니다...")
            
            logger.info(f"🚀 뉴스 수집 트리거됨 by {message.author.name}")
            
            # 현재 디렉토리 확인
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_script = os.path.join(script_dir, 'main.py')
            
            start_time = datetime.now()
            
            # main.py 실행
            result = subprocess.run(
                [sys.executable, main_script],
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                cwd=script_dir
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.last_execution = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 결과 처리
            if result.returncode == 0:
                # 성공
                await message.add_reaction('✅')
                
                success_msg = f"""✅ **Google News AI 뉴스 수집 완료!**

⏱️ **소요시간:** {duration:.1f}초
🕐 **완료시간:** {self.last_execution}
📊 **상태:** 성공

🔗 **결과 확인:**
• Notion 페이지에서 상세 내용 확인
• Telegram에서 요약 리포트 수신

다음 수집을 원하시면 언제든 `!뉴스`를 입력해주세요! 🚀"""
                
                await status_msg.edit(content=success_msg)
                
                logger.info(f"✅ 뉴스 수집 성공 - {duration:.1f}초 소요")
                
            else:
                # 실패
                await message.add_reaction('❌')
                
                error_msg = f"""❌ **뉴스 수집 실패**

⏱️ **소요시간:** {duration:.1f}초
🕐 **시도시간:** {self.last_execution}
❌ **오류코드:** {result.returncode}

🔧 **해결방법:**
1. 잠시 후 다시 시도해주세요
2. 계속 실패시 개발자에게 문의

**오류 로그:**
```
{result.stderr[:500] if result.stderr else '로그 없음'}
```"""
                
                await status_msg.edit(content=error_msg)
                
                logger.error(f"❌ 뉴스 수집 실패 - 코드: {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            await message.add_reaction('⏰')
            await status_msg.edit(content="⏰ **실행 시간 초과**\n\n5분이 경과하여 작업이 중단되었습니다. 네트워크 상태를 확인 후 다시 시도해주세요.")
            logger.error("⏰ 뉴스 수집 시간 초과")
            
        except Exception as e:
            await message.add_reaction('💥')
            await status_msg.edit(content=f"💥 **예상치 못한 오류**\n\n{str(e)}\n\n개발자에게 문의해주세요.")
            logger.error(f"💥 예상치 못한 오류: {e}")
            
        finally:
            # 실행 상태 해제
            self.is_running = False
    
    async def _send_status(self, message):
        """봇 상태 정보 전송"""
        status = "🔄 실행 중" if self.is_running else "⭐ 대기 중"
        
        status_msg = f"""📊 **Google News AI 봇 상태**

🤖 **현재 상태:** {status}
🕐 **마지막 실행:** {self.last_execution or '없음'}
📡 **모니터링 채널:** #{message.channel.name}
👤 **요청자:** {message.author.mention}

⚡ **사용 가능한 명령어:**
• `!뉴스`, `!news` - AI 뉴스 수집 실행
• `!상태`, `!status` - 현재 상태 확인  
• `!도움`, `!help` - 명령어 도움말

📋 **시스템 정보:**
• 프로젝트: {self.config.PROJECT_CODE}
• 버전: {self.config.SYSTEM_VERSION}
• 개발자: {self.config.DEVELOPER_NAME}"""
        
        await message.reply(status_msg)
    
    async def _send_help(self, message):
        """도움말 메시지 전송"""
        help_msg = f"""🆘 **Google News AI 봇 사용법**

⚡ **트리거 명령어:**
• `!뉴스` - AI 뉴스 수집 시작
• `!news` - AI 뉴스 수집 시작  
• `!ai뉴스` - AI 뉴스 수집 시작
• `!google뉴스` - AI 뉴스 수집 시작
• `!실행`, `!run` - AI 뉴스 수집 시작

📊 **정보 명령어:**
• `!상태`, `!status` - 봇 현재 상태 확인
• `!도움`, `!help` - 이 도움말 표시

🔄 **작동 방식:**
1. 위 명령어 중 하나를 채팅에 입력
2. 봇이 Google News에서 최신 AI 뉴스 수집
3. OpenAI로 뉴스 요약 생성  
4. Notion 데이터베이스에 저장
5. Telegram으로 결과 전송

⏱️ **소요시간:** 약 1-2분
🔄 **실행제한:** 동시 실행 불가 (순차 처리)

💡 **팁:** 메시지에 AI, 뉴스 관련 키워드만 포함해도 힌트를 받을 수 있어요!

🛠️ **개발자:** {self.config.DEVELOPER_NAME}
📧 **문의:** {self.config.DEVELOPER_EMAIL}"""
        
        await message.reply(help_msg)
    
    def run(self):
        """Discord 봇 실행"""
        if not self.bot_token:
            logger.error("❌ DISCORD_BOT_TOKEN이 설정되지 않았습니다!")
            print("❌ .env 파일에 DISCORD_BOT_TOKEN을 설정해주세요!")
            return False
        
        try:
            logger.info("🚀 Discord 트리거 봇 시작...")
            logger.info(f"📡 모니터링 채널 ID: {self.channel_id}")
            logger.info(f"🔑 트리거 키워드: {', '.join(self.trigger_keywords)}")
            
            self.client.run(self.bot_token)
            
        except discord.LoginFailure:
            logger.error("❌ Discord 로그인 실패! 토큰을 확인해주세요.")
            return False
        except Exception as e:
            logger.error(f"❌ Discord 봇 실행 오류: {e}")
            return False
    
    def test_connection(self):
        """연결 테스트"""
        if not self.bot_token:
            print("❌ DISCORD_BOT_TOKEN이 없습니다!")
            return False
        
        if not self.channel_id:
            print("❌ DISCORD_CHANNEL_ID가 없습니다!")
            return False
        
        print("✅ Discord 설정 확인 완료")
        print(f"📡 채널 ID: {self.channel_id}")
        print(f"🔑 트리거 키워드: {len(self.trigger_keywords)}개")
        return True

def main():
    """메인 실행"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            trigger = DiscordTrigger()
            trigger.test_connection()
            return
        elif sys.argv[1] == "help":
            print("사용법:")
            print("  python3 discord_trigger.py       # 디스코드 봇 시작")
            print("  python3 discord_trigger.py test  # 설정 테스트")
            print("  python3 discord_trigger.py help  # 도움말")
            return
    
    # Discord 트리거 봇 실행
    trigger = DiscordTrigger()
    trigger.run()

if __name__ == "__main__":
    main()
