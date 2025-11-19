import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tech_news():
    # GeekNews RSS (개발/테크 전용) - 품질이 좋음
    rss_url = "http://feeds.feedburner.com/geeknews-feed"
    
    # 만약 구글 뉴스를 선호하시면 아래 주석을 풀고 위 주소를 주석 처리하세요
    # rss_url = "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    
    if not feed.entries:
        return "뉴스 수집 실패"

    # 5개를 뽑아야 하므로 여유 있게 상위 15개를 가져와서 AI에게 던져줍니다.
    for entry in feed.entries[:15]:
        title = entry.title
        link = entry.link
        summary = getattr(entry, 'description', '')
        news_list.append(f"- 제목: {title}\n- 링크: {link}\n- 내용: {summary}\n")
        
    return "\n".join(news_list)

def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    너는 IT 테크 블로거야. 아래 뉴스 데이터 중에서 가장 중요하고 흥미로운 **Top 5** 이슈를 선정해줘.
    
    [뉴스 데이터]
    {news_data}
    
    [작성 포맷 - Markdown]
    1. 맨 윗줄에 인용구로 "> *이 포스팅은 Gemini AI가 선별하고 요약했습니다.*" 를 적어줘.
    2. 총 **5개**의 뉴스를 작성해야 해.
    3. **각 뉴스마다** 아래 형식을 엄격하게 지켜줘:
       
       ### [뉴스 제목]
       (여기에 뉴스 내용을 3~4문장으로 요약. 전문적인 어조로, 해요체 사용.)
       
       **[🔗 원문 기사 보기](뉴스링크)**
       
       (각 뉴스 사이에는 구분선 `---` 을 넣지 말고, 그냥 줄바꿈만 해줘.)
    
    4. **주의:** 맨 아래에 별도의 '출처' 섹션을 만들지 마. 출처 링크는 반드시 각 뉴스 요약 바로 밑에 위치해야 해.
    5. 전체적으로 깔끔한 마크다운 문법을 사용해.
    """
    
    # 모델 설정 (Gemini 2.5 Flash -> 실패시 Flash Latest)
    target_model = "gemini-2.5-flash"
    
    try:
        print(f"🤖 모델 사용 시도: {target_model}")
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"⚠️ 1차 시도 실패: {e}")
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
