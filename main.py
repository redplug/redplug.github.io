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
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Markdown 형식으로 요청
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
    response = model.generate_content(prompt)
    return response.text

def save_as_markdown(content):
    # 한국 시간 설정
    korea_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea_tz)
    
    # 1. 파일명 생성 (Jekyll 표준: YYYY-MM-DD-제목.md)
    # 제목에 공백이 있으면 안되므로 날짜로만 구성하거나 영문을 섞습니다.
    date_str = now.strftime("%Y-%m-%d")
    file_name = f"{date_str}-daily-it-news.md"
    
    # 2. Front Matter (Jekyll 헤더) 작성
    # 이것이 있어야 블로그가 글을 인식합니다.
    front_matter = f"""---
layout: post
title:  "[{now.strftime('%Y-%m-%d')}] 오늘의 주요 IT 뉴스 Top 3"
date:   {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: news
---

"""
    
    # 3. 파일 저장 ( _posts 폴더에 저장 )
    # _posts 폴더가 없으면 생성
    if not os.path.exists("_posts"):
        os.makedirs("_posts")
        
    file_path = os.path.join("_posts", file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
        
    print(f"✅ 파일 생성 완료: {file_path}")

if __name__ == "__main__":
    news = get_tech_news()
    content = generate_content(news)
    save_as_markdown(content)
