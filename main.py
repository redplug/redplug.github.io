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

    for entry in feed.entries[:15]:
        title = entry.title
        link = entry.link
        summary = getattr(entry, 'description', '')
        news_list.append(f"- 제목: {title}\n- 링크: {link}\n- 내용: {summary}\n")
        
    return "\n".join(news_list)

def generate_content(news_data):
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 프롬프트 수정: 서론 금지, 자체 푸터 금지
    prompt = f"""
    너는 IT 뉴스 큐레이터야. 아래 뉴스 데이터 중 Top 5를 선정해서 정리해줘.
    
    [뉴스 데이터]
    {news_data}
    
    [작성 규칙 - 엄격 준수]
    1. **서론, 인사말, 소개글을 절대 쓰지 마.** (예: "안녕하세요", "오늘은..." 금지)
    2. 바로 첫 번째 뉴스 제목부터 시작해.
    3. **글 맨 마지막에 '출처'나 '자동화 문구'를 절대 넣지 마.** (내가 코드로 넣을 거야)
    4. 총 **5개**의 뉴스를 작성해.
    
    [각 뉴스 작성 포맷]
    ### [뉴스 제목]
    
    **📌 요약**
    (뉴스 핵심 내용 3문장 내외)
    
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
    
    # [수정됨] 사용자가 원한 문구로 통합 & 디자인(인용구) 적용
    footer_text = "\n\n<br>\n\n> *이 포스팅은 Gemini AI가 제공한 뉴스 데이터를 기반으로 작성되었습니다.*"
    
    # AI가 혹시라도 서론을 썼을 경우를 대비해 앞뒤 공백 제거
    clean_content = content.strip()
    
    full_content = clean_content + footer_text
    
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
