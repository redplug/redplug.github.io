---
layout: default
title: Home
---

<style>
  /* 전체 다크 테마 설정 */
  :root {
    --bg-color: #121212;
    --card-bg: #1e1e1e;
    --text-main: #e0e0e0;
    --text-sub: #a0a0a0;
    --accent: #BB86FC; /* 보라색 포인트 */
    --accent-hover: #9965f4;
    --border: #333;
  }

  body {
    background-color: var(--bg-color) !important;
    color: var(--text-main) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }

  /* 헤더 & 푸터 강제 다크 모드 */
  .site-header, .site-footer {
    background-color: #000 !important;
    border-color: var(--border) !important;
  }
  .site-title, .site-nav .page-link {
    color: var(--accent) !important;
    font-weight: bold;
  }

  /* 메인 타이틀 섹션 */
  .hero-section {
    text-align: center;
    padding: 40px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 40px;
  }
  .hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #BB86FC, #03DAC6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
  }
  .hero-desc {
    color: var(--text-sub);
    font-size: 1.1rem;
  }

  /* 뉴스 카드 그리드 레이아웃 */
  .post-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
  }

  /* 카드 디자인 */
  .post-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 25px;
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
  }

  .post-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    border-color: var(--accent);
  }

  .post-date {
    font-size: 0.85rem;
    color: var(--text-sub);
    margin-bottom: 10px;
    display: block;
  }

  .post-title {
    font-size: 1.3rem;
    font-weight: bold;
    margin: 0 0 15px 0;
    line-height: 1.4;
  }

  .post-title a {
    color: var(--text-main) !important;
    text-decoration: none;
  }

  .post-excerpt {
    font-size: 0.95rem;
    color: var(--text-sub);
    line-height: 1.6;
    margin-bottom: 20px;
    flex-grow: 1; /* 내용이 짧아도 버튼을 바닥으로 밀어냄 */
  }

  .read-more {
    display: inline-block;
    padding: 8px 16px;
    background-color: rgba(187, 134, 252, 0.1);
    color: var(--accent) !important;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    transition: background 0.2s;
    text-align: center;
  }

  .read-more:hover {
    background-color: var(--accent);
    color: #000 !important;
    text-decoration: none;
  }

  /* 모바일 대응 */
  @media (max-width: 768px) {
    .post-grid {
      grid-template-columns: 1fr;
    }
    .hero-title {
      font-size: 2rem;
    }
  }
</style>

<div class="hero-section">
  <h1 class="hero-title">DAILY TECH BRIEF</h1>
  <p class="hero-desc">AI가 매일 정리해주는 IT 트렌드 인사이트</p>
</div>

<div class="post-grid">
  {% for post in site.posts limit:20 %}
    <div class="post-card">
      <div>
        <span class="post-date">{{ post.date | date: "%Y.%m.%d" }}</span>
        <h3 class="post-title">
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        </h3>
        <div class="post-excerpt">
          {{ post.excerpt | strip_html | truncate: 80 }}...
        </div>
      </div>
      <a href="{{ post.url | relative_url }}" class="read-more">Read News →</a>
    </div>
  {% endfor %}
</div>
