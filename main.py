import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tech_news():
    # 구글 뉴스 RSS (IT/기술)
    rss_url = "https://news.google.com/rss/topic/CAAqJggKIiBQQkFTRWdvSUwyMHZNRGRqTVhZU0FtdHZHZ0pMVWlnQVAB?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_list = []
    for entry in feed.entries[:10]:
        news_list.append(f"- 제목: {entry.title}\n- 링크: {entry.link}\n")
    return "\n".join(news_list)

def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    너는 IT 테크 블로거야. 아래 뉴스 중 Top 3를 선정해줘.
    
    [뉴스 리스트]
    {news_data}
    
    [작성 포맷 - Markdown]
    1. 맨 위에 "> *이 포스팅은 Gemini AI가 자동으로 작성했습니다.*" 를 인용구로 넣어.
    2. 각 이슈는 `### 제목` 으로 시작해.
    3. 내용은 요약, 시사점 위주로 작성해.
    4. 맨 아래에 `---` 를 넣고, `#### 출처` 섹션을 만들어 링크 리스트를 작성해.
    5. 전체적으로 깔끔한 마크다운 문법을 사용해.
    """
    
    # 1차 시도: Gemini 1.5 Flash (빠르고 저렴함)
    try:
        print("🤖 1차 시도: gemini-1.5-flash 모델 사용")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"⚠️ 1차 시도 실패 ({e})")
        print("🔄 2차 시도: gemini-pro 모델로 전환합니다.")
        
        # 2차 시도: Gemini Pro (가장 안정적임)
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"❌ 2차 시도도 실패했습니다: {e2}")
            return "AI 모델 호출에 실패하여 내용을 생성하지 못했습니다."

def save_as_markdown(content):
    korea_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea_tz)
    
    date_str = now.strftime("%Y-%m-%d")
    file_name = f"{date_str}-daily-it-news.md"
    
    front_matter = f"""---
layout: post
title:  "[{now.strftime('%Y-%m-%d')}] 오늘의 주요 IT 뉴스 Top 3"
date:   {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: news
---

"""
    
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
        
    file_path = os.path.join("_posts", file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
        
    print(f"✅ 파일 생성 완료: {file_path}")

if __name__ == "__main__":
    print("1. 뉴스 수집 중...")
    news = get_tech_news()
    
    print("2. AI 원고 작성 중...")
    content = generate_content(news)
    
    if "AI 모델 호출에 실패" not in content:
        print("3. 파일 저장 중...")
        save_as_markdown(content)
    else:
        print("❌ 콘텐츠 생성 실패로 저장을 건너뜁니다.")
        exit(1) # Action을 실패로 처리
