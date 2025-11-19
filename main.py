import os
import feedparser
import google.generativeai as genai
from datetime import datetime
import pytz

# --- 설정값 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tech_news():
    # [소스 리스트] 국내외 유력 IT RSS 5개 선정
    rss_sources = [
        # 1. GeekNews (한국 - 개발/테크)
        "http://feeds.feedburner.com/geeknews-feed",
        # 2. Google News IT (한국 - 종합)
        "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        # 3. Hacker News (해외 - 개발자 원픽)
        "https://news.ycombinator.com/rss",
        # 4. TechCrunch (해외 - 스타트업/비즈니스)
        "https://techcrunch.com/feed/",
        # 5. The Verge (해외 - 일반 IT/가전)
        "https://www.theverge.com/rss/index.xml"
    ]
    
    combined_news_list = []
    
    print("📡 뉴스 데이터 수집 중...")
    
    for url in rss_sources:
        try:
            feed = feedparser.parse(url)
            # 각 소스당 최신글 4개씩만 가져옴 (총 20개 후보군 생성)
            for entry in feed.entries[:4]:
                title = entry.title
                link = entry.link
                # 요약본이 있으면 가져오고 없으면 빈칸
                summary = getattr(entry, 'description', '')[:200] # 너무 길면 자름
                
                combined_news_list.append(f"Source: {url}\nTitle: {title}\nLink: {link}\nSummary: {summary}\n")
        except Exception as e:
            print(f"⚠️ {url} 수집 실패: {e}")
            continue

    # 후보군이 너무 적으면 실패 처리
    if len(combined_news_list) < 5:
        return "뉴스 수집 실패"
        
    return "\n---\n".join(combined_news_list)

def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 프롬프트 강화: 다국어 처리 및 번역 지시
    prompt = f"""
    너는 글로벌 IT 트렌드를 전하는 전문 에디터야.
    아래 제공된 뉴스 리스트는 한국어와 영어가 섞여 있어.
    이 중에서 **가장 중요하고 파급력 있는 Top 5 이슈**를 선정해줘.
    
    [뉴스 데이터 후보군]
    {news_data}
    
    [작성 규칙 - 엄격 준수]
    1. **서론, 인사말, 소개글 금지.** 바로 첫 번째 뉴스부터 시작해.
    2. **언어:** 모든 내용은 **반드시 '자연스러운 한국어'로 작성**해야 해. 
       - 영어 기사를 선정했다면, 내용을 완벽하게 한국어로 번역해서 요약해.
       - 제목도 한국 독자가 이해하기 쉽게 한국어로 의역해줘.
    3. **글 맨 마지막에 자동화 문구를 넣지 마.** (시스템이 처리함)
    
    [각 뉴스 작성 포맷]
    ### [한국어 뉴스 제목]
    
    **📌 요약**
    (뉴스 핵심 내용 3문장 내외. 영어권 뉴스라면 한국어로 번역해서 작성.)
    
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

def save_as_markdown(content):
    korea_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea_tz)
    
    date_str = now.strftime("%Y-%m-%d")
    file_name = f"{date_str}-daily-it-news.md"
    
    # 요청하신 고정 푸터 문구
    footer_text = "\n\n<br>\n\n> *이 포스팅은 Gemini AI가 제공한 뉴스 데이터를 기반으로 작성되었습니다.*"
    
    clean_content = content.strip()
    full_content = clean_content + footer_text
    
    front_matter = f"""---
layout: default
title:  "[{now.strftime('%Y-%m-%d')}] 오늘의 글로벌 IT 뉴스 Top 5"
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
    print("1. 멀티 소스 뉴스 수집 중...")
    news = get_tech_news()
    
    # 수집된 데이터가 너무 적으면 종료
    if news == "뉴스 수집 실패":
        print("❌ 수집된 뉴스가 부족하여 종료합니다.")
        exit(1)
    
    print("2. AI 원고 작성 및 번역 중...")
    content = generate_content(news)
    
    if content == "FAIL":
        print("❌ AI 모델 오류로 중단합니다.")
        exit(1)
    else:
        print("3. 파일 저장 중...")
        save_as_markdown(content)
