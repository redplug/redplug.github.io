import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tech_news():
    # GeekNews RSS 사용
    rss_url = "http://feeds.feedburner.com/geeknews-feed"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    
    if not feed.entries:
        return "뉴스 수집 실패"

    # 상위 15개 수집 후 AI에게 전달
    for entry in feed.entries[:15]:
        title = entry.title
        link = entry.link
        summary = getattr(entry, 'description', '')
        news_list.append(f"- 제목: {title}\n- 링크: {link}\n- 내용: {summary}\n")
        
    return "\n".join(news_list)

def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    너는 IT 테크 블로거야. 아래 뉴스 데이터 중 Top 5를 선정해줘.
    
    [뉴스 데이터]
    {news_data}
    
    [작성 포맷 - Markdown]
    1. 총 **5개**의 뉴스를 작성해.
    2. **각 뉴스마다** 아래 구조를 반드시 지켜줘 (헤더와 줄바꿈 필수):
       
       ### [뉴스 제목]
       
       **📌 요약**
       (여기에는 뉴스 내용을 3문장 내외로 핵심만 요약해서 작성)
       
       **💡 시사점**
       - (첫 번째 시사점: 기술적/산업적 파급효과)
       - (두 번째 시사점: 개발자나 업계에 미치는 영향)
       
       <br>
       **[🔗 원문 기사 보기]({{뉴스링크}})**
       
       ---
    
    3. **중요:** "이 포스팅은 Gemini AI가..." 같은 자동화 문구는 맨 위가 아니라, 글의 **맨 마지막**에 한 번만 넣어줘.
    4. 전체적으로 깔끔한 마크다운 문법을 사용해.
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
    
    # 맨 마지막에 자동화 문구 추가 (카드 미리보기 중복 방지용)
    footer_text = "\n\n<br>\n\n> *이 포스팅은 Gemini AI가 선별하고 요약했습니다.*"
    full_content = content + footer_text
    
    front_matter = f"""---
layout: default
title:  "[{now.strftime('%Y-%m-%d')}] 오늘의 IT 뉴스 Top 5"
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
