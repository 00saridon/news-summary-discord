import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAKAO_PENDING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kakao_pending.json')


def send_kakao_message(message):
    """메시지를 분할하고 파일로 저장 (Claude MCP가 읽어서 전송)"""
    try:
        messages = []
        if len(message) > 200:
            current_msg = ""
            for line in message.split('\n'):
                if len(current_msg) + len(line) + 1 > 190:
                    if current_msg:
                        messages.append(current_msg)
                    current_msg = line
                else:
                    current_msg += ('\n' + line) if current_msg else line
            if current_msg:
                messages.append(current_msg)
        else:
            messages = [message]

        with open(KAKAO_PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump({'messages': messages, 'status': 'pending'}, f, ensure_ascii=False, indent=2)

        logger.info(f"카카오톡 메시지 저장 완료: {len(messages)}개")
        return messages

    except Exception as e:
        logger.error(f"카카오톡 메시지 저장 오류: {e}")
        return None


def prepare_kakao_news_message(news_items, summary):
    """카카오톡 전송용 뉴스 요약 메시지 준비"""
    summary_lines = summary.split('\n')[:3]
    summary_text = '\n'.join(summary_lines)

    titles = '\n'.join([
        f"• {item['title'][:40]}..." if len(item['title']) > 40 else f"• {item['title']}"
        for item in news_items[:5]
    ])

    return f"📰 오늘의 뉴스요약\n\n{summary_text}\n\n주요기사:\n{titles}"


if __name__ == "__main__":
    from news_scraper import scrape_top_news
    from news_summarizer import summarize_news

    news_list = scrape_top_news()
    summary = summarize_news(news_list)

    if summary:
        message = prepare_kakao_news_message(news_list, summary)
        messages = send_kakao_message(message)
        for msg in messages:
            print(f"전송할 메시지:\n{msg}\n{'='*50}\n")
