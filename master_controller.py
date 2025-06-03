#!/usr/bin/env python3
# master_controller.py - 스케줄링 + 디스코드 트리거 통합 시스템

import asyncio
import schedule
import time
import threading
import subprocess
import sys
import os
import logging
from datetime import datetime

# 선택적 import (Discord 트리거)
try:
    from discord_trigger import DiscordTrigger
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️ discord_trigger.py가 없습니다. Discord 기능이 비활성화됩니다.")

from config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterController:
    """스케줄링 + 디스코드 트리거 통합 관리 시스템"""
    
    def __init__(self):
        self.config = Config
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_script = os.path.join(self.script_dir, 'main.py')
        
        # 실행 상태 관리
        self.is_running = False
        self.execution_history = []
        
        # Discord 트리거 봇
        self.discord_trigger = None
        
        # 스케줄 설정
        self.schedule_enabled = True
        self.discord_enabled = True
        
    def run_news_automation(self, trigger_source="schedule"):
        """뉴스 자동화 실행 (스케줄 또는 디스코드에서 호출)"""
        if self.is_running:
            logger.warning(f"⚠️ 이미 실행 중입니다. 요청 무시됨 (소스: {trigger_source})")
            return False
        
        try:
            self.is_running = True
            start_time = datetime.now()
            
            logger.info(f"🚀 Google News AI 자동화 시작 (트리거: {trigger_source})")
            logger.info(f"📍 실행 경로: {self.script_dir}")
            logger.info(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 작업 디렉토리 변경 후 main.py 실행
            os.chdir(self.script_dir)
            
            # Python 스크립트 실행
            result = subprocess.run(
                [sys.executable, 'main.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 실행 기록 저장
            execution_record = {
                'trigger': trigger_source,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'success': result.returncode == 0,
                'return_code': result.returncode
            }
            
            self.execution_history.append(execution_record)
            
            # 최근 10개만 유지
            if len(self.execution_history) > 10:
                self.execution_history = self.execution_history[-10:]
            
            if result.returncode == 0:
                logger.info("✅ Google News AI 자동화 성공")
                logger.info(f"⏱️ 소요시간: {duration:.1f}초")
                logger.info("📤 결과가 Notion과 Telegram으로 전송되었습니다")
                
                # 성공 시 결과 로그 (마지막 10줄만)
                if result.stdout:
                    logger.info("📋 실행 결과:")
                    for line in result.stdout.split('\n')[-10:]:
                        if line.strip():
                            logger.info(f"   {line}")
                
                return True
            else:
                logger.error("❌ Google News AI 자동화 실패")
                logger.error(f"Exit code: {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
                
                # 에러 알림
                self._send_error_notification(trigger_source, result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ 실행 시간 초과 (5분)")
            self._send_error_notification(trigger_source, "실행 시간 초과")
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            self._send_error_notification(trigger_source, str(e))
            return False
        finally:
            self.is_running = False
    
    def _send_error_notification(self, trigger_source, error_message):
        """에러 발생 시 텔레그램 알림"""
        try:
            error_script = f"""
import sys
sys.path.append('{self.script_dir}')
from telegram_sender import TelegramSender
telegram = TelegramSender()
telegram.send_error_notification('시스템 오류 (트리거: {trigger_source}): {error_message[:100]}')
"""
            subprocess.run([sys.executable, '-c', error_script], timeout=30)
        except Exception as e:
            logger.error(f"에러 알림 전송 실패: {e}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        if not self.schedule_enabled:
            logger.info("📅 스케줄 기능이 비활성화되어 있습니다")
            return
        
        # 매일 오전 7시 30분에 실행
        schedule.every().day.at("07:30").do(self.run_news_automation, trigger_source="schedule")
        
        logger.info("📅 스케줄 설정 완료:")
        logger.info("   • 실행 시간: 매일 오전 7시 30분")
        logger.info("   • 작업: Google News AI 자동화")
        logger.info("   • 결과: Notion + Telegram 자동 전송")
        
        # 다음 실행 시간 표시
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"   • 다음 실행: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def setup_discord_trigger(self):
        """Discord 트리거 설정"""
        if not self.discord_enabled:
            logger.info("🤖 Discord 트리거 기능이 비활성화되어 있습니다")
            return None
        
        if not DISCORD_AVAILABLE:
            logger.warning("⚠️ discord_trigger.py가 없습니다. Discord 기능 비활성화")
            self.discord_enabled = False
            return None
        
        # Discord 설정 확인
        discord_token = os.getenv('DISCORD_BOT_TOKEN')
        discord_channel = os.getenv('DISCORD_CHANNEL_ID')
        
        if not discord_token or not discord_channel:
            logger.warning("⚠️ Discord 설정이 없습니다. Discord 트리거 비활성화")
            logger.warning("   DISCORD_BOT_TOKEN 및 DISCORD_CHANNEL_ID를 .env에 설정하세요")
            self.discord_enabled = False
            return None
        
        # Discord 트리거 커스터마이징
        self.discord_trigger = DiscordTrigger()
        
        # 원본 트리거 메서드를 래핑하여 통합 관리
        original_trigger = self.discord_trigger._trigger_news_collection
        
        async def wrapped_trigger(message):
            """Discord 트리거를 Master Controller를 통해 실행"""
            try:
                # 실행 상태 확인
                if self.is_running:
                    await message.add_reaction('⏳')
                    await message.reply("🔄 현재 AI 뉴스 수집이 진행 중입니다. 잠시만 기다려주세요!")
                    return
                
                # 즉시 반응
                await message.add_reaction('🚀')
                status_msg = await message.reply("🚀 Google News AI 뉴스 수집을 시작합니다! 약 1-2분 소요될 예정입니다...")
                
                logger.info(f"🚀 Discord 트리거 수신: {message.author.name}")
                
                # Master Controller를 통해 실행
                success = self.run_news_automation(trigger_source="discord")
                
                # 결과 처리
                if success:
                    await message.add_reaction('✅')
                    
                    success_message = f"""✅ **Google News AI 뉴스 수집 완료!**

🕐 **완료시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 **상태:** 성공
🎯 **트리거:** Discord ({message.author.name})

🔗 **결과 확인:**
• Notion 페이지에서 상세 내용 확인
• Telegram에서 요약 리포트 수신

다음 수집을 원하시면 언제든 `!뉴스`를 입력해주세요! 🚀"""
                    
                    await status_msg.edit(content=success_message)
                    
                else:
                    await message.add_reaction('❌')
                    await status_msg.edit(content="❌ **뉴스 수집 실패**\n\n로그를 확인하거나 잠시 후 다시 시도해주세요.")
                
            except Exception as e:
                logger.error(f"❌ Discord 트리거 처리 오류: {e}")
                await message.add_reaction('💥')
                await message.reply(f"💥 오류가 발생했습니다: {str(e)}")
        
        # 트리거 메서드 교체
        self.discord_trigger._trigger_news_collection = wrapped_trigger
        
        logger.info("🤖 Discord 트리거 설정 완료:")
        logger.info(f"   • 봇 토큰: {'설정됨' if discord_token else '없음'}")
        logger.info(f"   • 채널 ID: {discord_channel}")
        logger.info(f"   • 트리거 키워드: {len(self.discord_trigger.trigger_keywords)}개")
        
        return self.discord_trigger
    
    def run_schedule_loop(self):
        """스케줄 루프 (별도 스레드에서 실행)"""
        logger.info("📅 스케줄 루프 시작")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except Exception as e:
            logger.error(f"❌ 스케줄 루프 오류: {e}")
    
    def get_status(self):
        """현재 상태 반환"""
        next_run = schedule.next_run()
        
        status = {
            'is_running': self.is_running,
            'schedule_enabled': self.schedule_enabled,
            'discord_enabled': self.discord_enabled,
            'next_scheduled_run': next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else None,
            'execution_history': self.execution_history[-5:],  # 최근 5개
            'total_executions': len(self.execution_history)
        }
        
        return status
    
    def print_status(self):
        """상태 출력"""
        status = self.get_status()
        
        print("\n📊 Master Controller 상태:")
        print("=" * 50)
        print(f"🔄 현재 실행 상태: {'실행 중' if status['is_running'] else '대기 중'}")
        print(f"📅 스케줄 기능: {'활성화' if status['schedule_enabled'] else '비활성화'}")
        print(f"🤖 Discord 트리거: {'활성화' if status['discord_enabled'] else '비활성화'}")
        
        if status['next_scheduled_run']:
            print(f"⏰ 다음 스케줄 실행: {status['next_scheduled_run']}")
        
        print(f"📋 총 실행 횟수: {status['total_executions']}회")
        
        if status['execution_history']:
            print("\n📈 최근 실행 이력:")
            for i, record in enumerate(status['execution_history'], 1):
                result = "✅ 성공" if record['success'] else "❌ 실패"
                print(f"  {i}. {record['start_time'].strftime('%m-%d %H:%M')} | {record['trigger']} | {result} | {record['duration']:.1f}s")
    
    def run(self):
        """마스터 컨트롤러 실행"""
        logger.info("🚀 Master Controller 시작")
        logger.info("=" * 60)
        logger.info(f"🔧 프로젝트: {self.config.PROJECT_CODE}")
        logger.info(f"⚙️ 시스템: {self.config.SYSTEM_NAME} {self.config.SYSTEM_VERSION}")
        
        # 스케줄 설정
        self.setup_schedule()
        
        # Discord 트리거 설정
        discord_trigger = self.setup_discord_trigger()
        
        print("\n🎯 실행 방법:")
        print("=" * 50)
        if self.schedule_enabled:
            next_run = schedule.next_run()
            if next_run:
                print(f"📅 자동 실행: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.discord_enabled and discord_trigger:
            print("🤖 Discord 트리거: 디스코드 채널에 '!뉴스' 입력")
        
        print("⚡ 수동 실행: python3 main.py")
        print("📊 상태 확인: Ctrl+C 후 'status' 명령어")
        
        try:
            if self.schedule_enabled and self.discord_enabled and DISCORD_AVAILABLE and discord_trigger:
                # 둘 다 활성화된 경우: 스케줄은 별도 스레드, Discord는 메인 스레드
                logger.info("🔄 스케줄 + Discord 통합 모드 시작")
                
                # 스케줄 스레드 시작
                schedule_thread = threading.Thread(target=self.run_schedule_loop, daemon=True)
                schedule_thread.start()
                logger.info("📅 스케줄 스레드 시작됨")
                
                # Discord 봇 실행 (메인 스레드)
                logger.info("🤖 Discord 봇 시작...")
                discord_trigger.run()
                
            elif self.schedule_enabled:
                # 스케줄만 활성화
                logger.info("📅 스케줄 전용 모드 시작")
                self.run_schedule_loop()
                
            elif self.discord_enabled and DISCORD_AVAILABLE and discord_trigger:
                # Discord만 활성화
                logger.info("🤖 Discord 전용 모드 시작")
                discord_trigger.run()
                
            else:
                logger.warning("⚠️ 스케줄과 Discord 모두 비활성화 또는 사용 불가")
                print("📅 스케줄 전용 모드로 실행합니다...")
                self.schedule_enabled = True
                self.run_schedule_loop()
                
        except KeyboardInterrupt:
            logger.info("⏹️ Master Controller 종료")
            self.print_status()
        except Exception as e:
            logger.error(f"❌ Master Controller 오류: {e}")
            return False
        
        return True

def main():
    """메인 실행"""
    import sys
    
    controller = MasterController()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("🧪 즉시 테스트 실행")
            success = controller.run_news_automation(trigger_source="manual_test")
            if success:
                print("✅ 테스트 성공")
            else:
                print("❌ 테스트 실패")
            return
        elif sys.argv[1] == "status":
            controller.print_status()
            return
        elif sys.argv[1] == "schedule-only":
            controller.discord_enabled = False
            print("📅 스케줄 전용 모드")
        elif sys.argv[1] == "discord-only":
            controller.schedule_enabled = False
            print("🤖 Discord 전용 모드")
        elif sys.argv[1] == "help":
            print("사용법:")
            print("  python3 master_controller.py              # 스케줄 + Discord 통합 실행")
            print("  python3 master_controller.py test         # 즉시 테스트 실행")
            print("  python3 master_controller.py status       # 상태 확인")
            print("  python3 master_controller.py schedule-only # 스케줄만 실행")
            print("  python3 master_controller.py discord-only  # Discord만 실행")
            print("  python3 master_controller.py help         # 도움말")
            return
    
    # Master Controller 실행
    controller.run()

if __name__ == "__main__":
    main()
