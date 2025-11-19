---
layout: default
title: Redplug Blog
---

# 📰 오늘의 IT 뉴스

최신 기술 뉴스를 AI가 매일 정리해드립니다.

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
      <span style="color: #888; font-size: 0.8em;">({{ post.date | date: "%Y-%m-%d" }})</span>
    </li>
  {% endfor %}
</ul>
