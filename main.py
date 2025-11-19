import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tech_news():
    # GeekNews RSS (개발/테크 전용)
    rss_url = "http://feeds.feedburner.com/geeknews-feed"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    
    if not feed.entries:
        print("⚠️ 뉴스 피드를 가져오지 못했습니다.")
        return "뉴스 수집 실패"

    for entry in feed.entries[:10]:
        # GeekNews는 요약문(description)도 품질이 좋아서 같이 넘겨주면 Gemini가 더 잘 씁니다.
        title = entry.title
        link = entry.link
        summary = getattr(entry, 'description', '') # 요약이 있으면 가져옴
        
        news_list.append(f"- 제목: {title}\n- 링크: {link}\n- 내용: {summary}\n")
        
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
    
    # 리스트에 있는 최신 모델 사용 (gemini-2.5-flash)
    target_model = "gemini-2.5-flash"
    
    try:
        print(f"🤖 모델 사용 시도: {target_model}")
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"⚠️ 1차 시도 실패: {e}")
        
        # 백업: 가장 최신 플래시 모델을 자동으로 잡는 별칭 사용
        fallback_model = "gemini-flash-latest"
        print(f"🔄 2차 시도: {fallback_model}로 전환합니다.")
        try:
            model = genai.GenerativeModel(fallback_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e2:
            print(f"❌ 2차 시도 실패: {e2}")
            return "FAIL"

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
    
    if content == "FAIL":
        print("❌ AI 모델 오류로 중단합니다.")
        exit(1)
    else:
        print("3. 파일 저장 중...")
        save_as_markdown(content)
