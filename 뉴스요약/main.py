"""
네이버 뉴스(정치/경제) Gemini 요약 및 디스코드/카카오톡 전송 프로그램

기능:
  - 네이버 뉴스 정치(100), 경제(101), 문화(103) 섹션 수집
  - Gemini를 통한 섹션별 요약
  - 디스코드 웹훅 1번(정치), 2번(경제), 3번(문화) 분리 전송
  - 카카오톡 전송용 메시지를 kakao_pending.json으로 저장 (Claude MCP가 전송)

사용방법:
  python main.py                    # 기본 실행 (디스코드 전송)
  python main.py --preview          # 미리보기 (전송 안함)
  python main.py --kakao-only       # 카카오톡용 메시지 파일 저장
"""

import sys
import logging
import requests
from datetime import datetime
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def summarize_with_gemini(news_content, category_name):
    """Gemini 모델로 특정 카테고리 뉴스 요약"""
    try:
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            logger.error("GOOGLE_GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
            return None

        client = genai.Client(api_key=api_key)
        
        prompt = f"""다음은 네이버 뉴스의 {category_name} 섹션 헤드라인입니다.
이 뉴스들을 분석하고 주요 내용을 요약해주세요.

{news_content}

요약 형식:
1. 주요 {category_name} 뉴스 요약 (3-5개)
2. 종합적인 오늘의 {category_name} 트렌드 및 시사점 (3-5줄)"""

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        logger.info(f"✅ Gemini {category_name} 요약 완료")
        return response.text

    except Exception as e:
        logger.error(f"Gemini 요약 중 오류: {e}")
        return None


def run_news_summary(discord_only=False, preview=False):
    """뉴스 요약 및 전송 실행"""

    logger.info("=" * 80)
    logger.info("Gemini를 이용한 뉴스 요약 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # 1. 네이버 뉴스 수집 (정치: 100, 경제: 101, 문화: 103)
    logger.info("1단계: 네이버 뉴스 정치(100), 경제(101), 문화(103) 뉴스 수집 중...")

    from news_scraper import scrape_naver_news

    politics_news = scrape_naver_news('100')
    economy_news = scrape_naver_news('101')
    culture_news = scrape_naver_news('103')

    all_news_items = politics_news[:10] + economy_news[:10] + culture_news[:10]

    if not all_news_items:
        logger.error("뉴스 수집 실패")
        return False
        
    # 2. Gemini로 각각 요약
    logger.info("2단계: 정치, 경제, 문화 뉴스 각각 요약 중...")

    politics_content = "정치 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in politics_news[:10]])
    economy_content = "경제 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in economy_news[:10]])
    culture_content = "문화 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in culture_news[:10]])

    politics_summary = summarize_with_gemini(politics_content, "정치")
    economy_summary = summarize_with_gemini(economy_content, "경제")
    culture_summary = summarize_with_gemini(culture_content, "문화")

    if not politics_summary and not economy_summary and not culture_summary:
        logger.error("뉴스 요약에 모두 실패했습니다")
        return False

    # 3. 미리보기 (전송 안함)
    if preview:
        print("\n" + "=" * 80)
        print("정치 뉴스 요약:")
        print(politics_summary or "실패")
        print("-" * 40)
        print("경제 뉴스 요약:")
        print(economy_summary or "실패")
        print("-" * 40)
        print("문화 뉴스 요약:")
        print(culture_summary or "실패")
        print("=" * 80)
        return True

    # 3. 디스코드 전송
    logger.info("3단계: 디스코드 웹훅별 전송 중...")
    
    success_politics = False
    success_economy = False
    success_culture = False

    if politics_summary:
        success_politics = send_to_single_webhook(os.getenv('DISCORD_WEBHOOK_1'), "⚖️ 오늘의 정치 뉴스 요약", politics_summary)

    if economy_summary:
        success_economy = send_to_single_webhook(os.getenv('DISCORD_WEBHOOK_2'), "💰 오늘의 경제 뉴스 요약", economy_summary)

    if culture_summary:
        success_culture = send_to_single_webhook(os.getenv('DISCORD_WEBHOOK_3'), "🎭 오늘의 문화 뉴스 요약", culture_summary)

    if success_politics:
        logger.info("✅ 정치 뉴스 전송 완료 (웹훅 1)")
    if success_economy:
        logger.info("✅ 경제 뉴스 전송 완료 (웹훅 2)")
    if success_culture:
        logger.info("✅ 문화 뉴스 전송 완료 (웹훅 3)")

    logger.info("=" * 80)
    logger.info("모든 작업 완료!")
    logger.info("=" * 80)

    return True


def send_to_single_webhook(webhook_url, title, content):
    """단일 디스코드 웹훅에 전송"""
    if not webhook_url:
        logger.error("웹훅 URL이 설정되지 않았습니다")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": content[:4000],
                "color": 0x3498db if "정치" in title else (0xe74c3c if "경제" in title else 0x9b59b6)
            }
        ]
    }

    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        return r.status_code == 204
    except Exception as e:
        logger.error(f"디스코드 전송 중 오류: {e}")
        return False


def summarize_for_kakao(news_content, category_name):
    """카카오톡 한 단락 형식으로 요약 (2문장 + 해시태그, 160자 이내)"""
    try:
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            return None

        client = genai.Client(api_key=api_key)

        prompt = f"""다음 {category_name} 뉴스 헤드라인을 카카오톡 메시지 한 단락으로 요약하세요.

{news_content}

규칙:
- 오늘의 핵심 흐름만 2문장 이내로 (총 130자 이내)
- 마지막 줄에 핵심 키워드 해시태그 3~4개
- 마크다운(**, ###, *, -)은 절대 사용하지 않음
- 제목이나 부연 설명 없이 바로 요약문 시작

출력 예시:
오늘 여야는 특검 법안을 두고 강대강 대치를 이어갔다. 국방장관은 전작권 논의를 위해 방미했다.
#여야대립 #특검 #한미동맹"""

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        logger.info(f"✅ Gemini {category_name} 카카오 요약 완료")
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini 카카오 요약 오류: {e}")
        return None


def run_kakao_summary():
    """뉴스 수집/요약 후 kakao_pending.json에 저장 (Claude MCP가 전송)"""
    from news_scraper import scrape_naver_news
    from kakao_sender import save_kakao_messages

    logger.info("=" * 80)
    logger.info("카카오톡용 뉴스 요약 시작")
    logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    logger.info("1단계: 뉴스 수집 중...")
    politics_news = scrape_naver_news('100')
    economy_news = scrape_naver_news('101')
    culture_news = scrape_naver_news('103')

    if not politics_news and not economy_news and not culture_news:
        logger.error("뉴스 수집 실패")
        return False

    logger.info("2단계: Gemini 카카오 전용 요약 중...")
    politics_content = "정치 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in politics_news[:10]])
    economy_content = "경제 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in economy_news[:10]])
    culture_content = "문화 뉴스 헤드라인:\n" + "\n".join([f"- {item['title']}" for item in culture_news[:10]])

    politics_summary = summarize_for_kakao(politics_content, "정치")
    economy_summary = summarize_for_kakao(economy_content, "경제")
    culture_summary = summarize_for_kakao(culture_content, "문화")

    if not politics_summary and not economy_summary and not culture_summary:
        logger.error("모든 요약 실패")
        return False

    logger.info("3단계: kakao_pending.json 저장 중...")
    date_str = datetime.now().strftime('%Y년 %m월 %d일')

    messages = [f"📰 {date_str} 뉴스 요약"]
    if politics_summary:
        messages.append(f"⚖️ 정치\n{politics_summary}")
    if economy_summary:
        messages.append(f"💰 경제\n{economy_summary}")
    if culture_summary:
        messages.append(f"🎭 문화\n{culture_summary}")

    result = save_kakao_messages(messages)
    if result:
        logger.info(f"✅ kakao_pending.json 저장 완료 ({len(messages)}개 메시지)")
        return True
    return False


def main():
    """메인 함수"""
    kakao_only = '--kakao-only' in sys.argv
    discord_only = '--discord-only' in sys.argv
    preview = '--preview' in sys.argv

    try:
        if kakao_only:
            success = run_kakao_summary()
        else:
            success = run_news_summary(
                discord_only=discord_only,
                preview=preview
            )
        return success

    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
