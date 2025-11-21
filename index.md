---
layout: default
title: Home
---

<div style="text-align: center; padding: 30px 0;">
  <h1 style="background: linear-gradient(90deg, #BB86FC, #03DAC6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 800; margin: 0 0 10px 0;">DAILY TECH BRIEF</h1>
  <p style="color: #a0a0a0;">AI가 매일 정리해주는 IT 트렌드 인사이트</p>
</div>

<div class="post-grid">
  {% for post in site.posts %}
    <div class="post-card">

      <h3 class="post-title">
        <a href="{{ post.url }}">{{ post.title }}</a>
      </h3>
      <div class="post-excerpt">
        {{ post.excerpt | strip_html | truncate: 80 }}...
      </div>
      <a href="{{ post.url }}" class="read-more">Read News →</a>
    </div>
  {% else %}
    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #888;">
      <h3>⏳ 아직 발행된 뉴스가 없습니다.</h3>
      <p>내일 오후 12시에 첫 뉴스가 발행됩니다.</p>
    </div>
  {% endfor %}
</div>
