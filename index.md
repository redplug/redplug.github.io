---
layout: default
title: Home
---

<div style="text-align: center; margin-bottom: 40px;">
  <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; background: linear-gradient(90deg, #BB86FC, #03DAC6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DAILY TECH BRIEF</h1>
  <p style="color: #a0a0a0; font-size: 1.1rem;">AI가 매일 정리해주는 IT 트렌드 인사이트</p>
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
