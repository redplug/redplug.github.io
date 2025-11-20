import os
import json
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# --- 1. 뉴스 수집 (멀티 소스) ---
def get_tech_news():
    rss_sources = [
        "http://feeds.feedburner.com/geeknews-feed",
        "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.ycombinator.com/rss",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml"
    ]
    
    combined_news_list = []
    print("📡 뉴스 데이터 수집 중...")
    
    for url in rss_sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                title = entry.title
                link = entry.link
                summary = getattr(entry, 'description', '')[:200]
                combined_news_list.append(f"Source: {url}\nTitle: {title}\nLink: {link}\nSummary: {summary}\n")
        except Exception as e:
            print(f"⚠️ {url} 수집 실패: {e}")
            continue

    if len(combined_news_list) < 5:
        return "뉴스 수집 실패"
        
    return "\n---\n".join(combined_news_list)

# --- 2. AI 원고 작성 ---
def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    너는 글로벌 IT 트렌드를 전하는 전문 에디터야.
    아래 뉴스 리스트에서 가장 중요하고 파급력 있는 **Top 5 이슈**를 선정해줘.
    
    [뉴스 데이터]
    {news_data}
    
    [작성 규칙]
    1. **서론, 인사말, 소개글 금지.** 바로 첫 번째 뉴스부터 시작해.
    2. **언어:** 내용은 반드시 **'자연스러운 한국어'**로 작성해. (영어 기사는 번역 필수)
    3. **글 맨 마지막에 자동화 문구를 넣지 마.**
    
    [각 뉴스 작성 포맷]
    ### [한국어 뉴스 제목]
    
    **📌 요약**
    (핵심 내용 3문장 내외)
    
    **💡 시사점**
    - (시사점 1)
    - (시사점 2)
    
    <br>
    **[🔗 원문 기사 보기]({{뉴스링크}})**
    
    ---
    """
    
    target_model = "gemini-2.5-flash"
    
    try:
        print(f"🤖 모델 사용 시도: {target_model}")
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ 1차 시도 실패: {e}")
        fallback_model = "gemini-flash-latest"
        try:
            print(f"🔄 2차 시도: {fallback_model}")
            model = genai.GenerativeModel(fallback_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"❌ 2차 시도 실패: {e2}")
            return "FAIL"

# --- 3. Slack 알림 전송 ---
def send_slack_notification(title, blog_url):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack URL이 설정되지 않아 알림을 건너뜁니다.")
        return
        
    message = {
        "text": f"📢 *[새 글 발행]* {title}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📢 *새로운 IT 뉴스가 블로그에 업로드되었습니다!*\n\n*<{blog_url}|{title}>*\n\n오늘의 핵심 이슈 Top 5를 확인해보세요. 🚀"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 발행일: {datetime.now().strftime('%Y-%m-%d')}"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        if response.status_code == 200:
            print("✅ Slack 알림 전송 성공")
        else:
            print(f"❌ Slack 전송 실패: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Slack 에러 발생: {e}")

# --- 4. 파일 저장 및 메인 실행 ---
def save_as_markdown(content):
    korea_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea_tz)
    
    date_str = now.strftime("%Y-%m-%d")
    file_name = f"{date_str}-daily-it-news.md"
    post_title = f"[{now.strftime('%Y-%m-%d')}] 오늘의 글로벌 IT 뉴스 Top 5"
    
    footer_text = "\n\n<br>\n\n> *이 포스팅은 Gemini AI가 제공한 뉴스 데이터를 기반으로 작성되었습니다.*"
    
    full_content = content.strip() + footer_text
    
    front_matter = f"""---
layout: default
title:  "{post_title}"
date:   {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: news
---

"""
    
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
        
    file_path = os.path.join("_posts", file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(front_matter + full_content)
        
    print(f"✅ 파일 생성 완료: {file_path}")
    
    # 파일 생성이 성공하면 Slack 알림 발송
    # 블로그 메인 주소 (본인 주소로 수정 가능하나 기본적으로 github.io 사용)
    blog_url = "https://redplug.github.io" 
    send_slack_notification(post_title, blog_url)

if __name__ == "__main__":
    print("1. 멀티 소스 뉴스 수집 중...")
    news = get_tech_news()
    
    if news == "뉴스 수집 실패":
        print("❌ 수집 실패로 종료")
        exit(1)
    
    print("2. AI 원고 작성 중...")
    content = generate_content(news)
    
    if content == "FAIL":
        print("❌ AI 오류로 종료")
        exit(1)
    else:
        print("3. 파일 저장 및 알림 전송...")
        save_as_markdown(content)
