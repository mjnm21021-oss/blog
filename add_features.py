#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブログ記事に5つの機能を一括追加:
1. パンくずリスト
2. 読了時間
3. SNSシェアボタン
4. 関連記事
5. 404ページ（別途作成）
"""

import os
import re
from pathlib import Path

# 記事のカテゴリ分類
CATEGORIES = {
    'news': {
        'label': '海外AI',
        'articles': ['news-shumer', 'news-ai-cartel', 'news-nvidia-dms', 'news-shumer-rebuttal', 
                     'news-solo-founder', 'news-vending-machine', 'news-klarna', 'news-ai-finance']
    },
    'tech': {
        'label': 'ブログ',
        'articles': ['day1', 'soul-md-merged', 'comfyui', 'morning-briefing', 
                     'token-efficiency', 'cron-heartbeat', 'multi-agent-flow']
    },
    'backtest': {
        'label': 'バックテスト',
        'articles': ['backtest-overview', 'backtest-failures', 'backtest-method']
    }
}

# 各記事の情報（タイトル、読了時間、説明）
ARTICLE_INFO = {
    'news-shumer': {
        'title': 'Xで8100万回読まれたAI起業家の話',
        'desc': 'HyperWrite CEOが「もう自分の仕事、いらなくなった」と書いたエッセイ',
        'reading_time': 3
    },
    'news-ai-cartel': {
        'title': 'AIカルテル自販機実験',
        'desc': 'AIに「利益最大化」を任せたら勝手にカルテルを組んだ話',
        'reading_time': 4
    },
    'news-nvidia-dms': {
        'title': 'NVIDIA DMSの衝撃',
        'desc': 'AIの推論速度が30倍高速化された技術の話',
        'reading_time': 3
    },
    'news-shumer-rebuttal': {
        'title': 'AI起業家への反論記事',
        'desc': 'Matt Shumerの主張に対する懐疑的な視点',
        'reading_time': 3
    },
    'news-solo-founder': {
        'title': 'ソロ起業家の時代',
        'desc': '一人でスタートアップを立ち上げるAI時代の起業',
        'reading_time': 4
    },
    'news-vending-machine': {
        'title': '自販機AI価格実験',
        'desc': 'AIが需要予測して価格を自動調整する自販機の話',
        'reading_time': 3
    },
    'news-klarna': {
        'title': 'Klarnaの生成AI導入',
        'desc': 'フィンテック企業が700人分の仕事をAIに置き換えた話',
        'reading_time': 3
    },
    'news-ai-finance': {
        'title': 'AI×金融の最前線',
        'desc': '金融業界におけるAI活用の最新動向',
        'reading_time': 4
    },
    'day1': {
        'title': 'Day1: チーム構築',
        'desc': 'OpenClawでAIエージェントチームを立ち上げた初日の記録',
        'reading_time': 5
    },
    'soul-md-merged': {
        'title': 'SOUL.md: AI臭さ対策',
        'desc': 'AIエージェントの出力を自然にするSOUL.mdの仕組み',
        'reading_time': 4
    },
    'comfyui': {
        'title': 'ComfyUI: ローカル自動化',
        'desc': 'ローカルで動く画像生成AIの自動化環境',
        'reading_time': 5
    },
    'morning-briefing': {
        'title': '朝ブリーフィング自動化',
        'desc': 'OpenClawのcronで毎朝の情報収集を自動化した話',
        'reading_time': 4
    },
    'token-efficiency': {
        'title': 'トークン効率化',
        'desc': 'AIエージェントのコスト削減とパフォーマンス改善',
        'reading_time': 5
    },
    'cron-heartbeat': {
        'title': 'cron + heartbeat',
        'desc': '定期タスクと動的チェックを組み合わせた自動化',
        'reading_time': 4
    },
    'multi-agent-flow': {
        'title': 'マルチエージェント連携',
        'desc': '複数のAIエージェントを協調させる設計パターン',
        'reading_time': 5
    },
    'backtest-overview': {
        'title': 'トレードシステム概要編',
        'desc': 'AIエージェントによる自動トレードシステムの全体像',
        'reading_time': 6
    },
    'backtest-failures': {
        'title': 'トレードシステム失敗編',
        'desc': 'バックテストで失敗から学んだ教訓',
        'reading_time': 5
    },
    'backtest-method': {
        'title': 'トレードシステム仕組み編',
        'desc': 'トレードシステムの技術的な実装方法',
        'reading_time': 6
    }
}

def get_category(article_slug):
    """記事のカテゴリを取得"""
    for cat_key, cat_data in CATEGORIES.items():
        if article_slug in cat_data['articles']:
            return cat_key, cat_data['label']
    return None, None

def get_related_articles(article_slug, max_count=3):
    """関連記事を取得（同じカテゴリから2-3本）"""
    cat_key, _ = get_category(article_slug)
    if not cat_key:
        return []
    
    same_category = [a for a in CATEGORIES[cat_key]['articles'] if a != article_slug]
    
    # 優先順位: news系は最新記事、tech系は人気記事
    if cat_key == 'news':
        same_category = same_category[:max_count]
    elif cat_key == 'tech':
        # token-efficiency, multi-agent-flow, morning-briefing を優先
        priority = ['token-efficiency', 'multi-agent-flow', 'morning-briefing']
        related = [a for a in priority if a in same_category]
        related += [a for a in same_category if a not in priority]
        same_category = related[:max_count]
    else:  # backtest
        same_category = same_category[:max_count]
    
    return same_category[:max_count]

def create_breadcrumb(article_slug):
    """パンくずリストHTMLを生成"""
    cat_key, cat_label = get_category(article_slug)
    article_title = ARTICLE_INFO.get(article_slug, {}).get('title', article_slug)
    
    breadcrumb_html = f'''
<!-- パンくずリスト -->
<nav class="breadcrumb" aria-label="Breadcrumb">
  <a href="../">Home</a> &gt; <span>{cat_label}</span> &gt; <span class="current">{article_title}</span>
</nav>

<style>
.breadcrumb {{
  font-size: 12px;
  color: #999;
  padding: 8px 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}}
.breadcrumb a {{
  color: #e63946;
  text-decoration: none;
}}
.breadcrumb a:hover {{
  text-decoration: underline;
}}
.breadcrumb .current {{
  color: #333;
}}
</style>

<!-- Schema.org BreadcrumbList -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://daisuki-koshian.github.io/blog/"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{cat_label}",
      "item": "https://daisuki-koshian.github.io/blog/#"
    }},
    {{
      "@type": "ListItem",
      "position": 3,
      "name": "{article_title}",
      "item": "https://daisuki-koshian.github.io/blog/{article_slug}/"
    }}
  ]
}}
</script>
'''
    return breadcrumb_html

def create_reading_time(article_slug):
    """読了時間HTMLを生成"""
    reading_time = ARTICLE_INFO.get(article_slug, {}).get('reading_time', 3)
    
    return f'''
<div class="reading-time" style="font-size: 13px; color: #999; text-align: center; margin: 24px 0; padding: 12px; background: #f9f9f9; border-radius: 4px;">
  ⏱ 約{reading_time}分で読めます
</div>
'''

def create_share_buttons(article_slug):
    """SNSシェアボタンHTMLを生成"""
    article_title = ARTICLE_INFO.get(article_slug, {}).get('title', article_slug)
    article_url = f"https://daisuki-koshian.github.io/blog/{article_slug}/"
    
    import urllib.parse
    encoded_url = urllib.parse.quote(article_url)
    encoded_title = urllib.parse.quote(article_title)
    
    share_html = f'''
<!-- SNSシェアボタン -->
<div class="share-buttons">
  <p class="share-title">この記事をシェア</p>
  <div class="share-buttons-inner">
    <a href="https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}&via=daisuki_koshian" 
       target="_blank" rel="noopener" class="share-btn share-btn-x">
      <span class="share-icon">𝕏</span> Xでシェア
    </a>
    <a href="https://b.hatena.ne.jp/entry/{encoded_url}" 
       target="_blank" rel="noopener" class="share-btn share-btn-hatena">
      <span class="share-icon">B!</span> はてブ
    </a>
  </div>
</div>

<style>
.share-buttons {{
  margin: 40px 0;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
  text-align: center;
}}
.share-title {{
  font-size: 14px;
  font-weight: 700;
  color: #666;
  margin-bottom: 16px;
}}
.share-buttons-inner {{
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}}
.share-btn {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.share-btn:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}
.share-btn-x:hover {{
  background: #000;
  color: #fff;
  border-color: #000;
}}
.share-btn-hatena:hover {{
  background: #00A4DE;
  color: #fff;
  border-color: #00A4DE;
}}
.share-icon {{
  font-size: 18px;
}}
</style>
'''
    return share_html

def create_related_articles(article_slug):
    """関連記事セクションHTMLを生成"""
    related = get_related_articles(article_slug, 3)
    
    if not related:
        return ""
    
    cards_html = ""
    for rel_slug in related:
        rel_info = ARTICLE_INFO.get(rel_slug, {})
        rel_title = rel_info.get('title', rel_slug)
        rel_desc = rel_info.get('desc', '')
        
        cards_html += f'''
        <a href="../{rel_slug}/" class="related-card">
          <div class="related-card-title">{rel_title}</div>
          <div class="related-card-desc">{rel_desc}</div>
        </a>
'''
    
    related_html = f'''
<!-- 関連記事 -->
<div class="related-articles">
  <h3 class="related-title">関連記事</h3>
  <div class="related-cards">
{cards_html}
  </div>
</div>

<style>
.related-articles {{
  margin: 48px 0;
  padding: 32px;
  background: #fafafa;
  border-radius: 8px;
}}
.related-title {{
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}}
.related-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}}
.related-card {{
  display: block;
  padding: 16px;
  background: #fff;
  border-left: 3px solid #e63946;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.related-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}
.related-card-title {{
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}}
.related-card-desc {{
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}}
@media (max-width: 768px) {{
  .related-cards {{
    grid-template-columns: 1fr;
  }}
}}
</style>
'''
    return related_html

def process_article(article_dir):
    """1つの記事を処理"""
    article_slug = os.path.basename(article_dir)
    index_path = os.path.join(article_dir, 'index.html')
    
    if not os.path.exists(index_path):
        print(f"⚠️  {article_slug}: index.html not found")
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 既に処理済みかチェック
    if '<!-- パンくずリスト -->' in html:
        print(f"✓ {article_slug}: already processed")
        return False
    
    # 1. パンくずリスト（<div class="hero">の直前）
    breadcrumb = create_breadcrumb(article_slug)
    html = html.replace('<div class="hero">', f'{breadcrumb}\n<div class="hero">')
    
    # 2. 読了時間（</div><!-- /hero -->の直後、<div class="content-wrapper">の前）
    reading_time = create_reading_time(article_slug)
    hero_end = '</div>\n</div>\n\n<div class="content-wrapper">'
    if hero_end in html:
        html = html.replace(hero_end, f'</div>\n</div>\n{reading_time}\n<div class="content-wrapper">')
    else:
        # 別パターンを試す
        hero_end_alt = '</div>\n\n<div class="content-wrapper">'
        if hero_end_alt in html:
            html = html.replace(hero_end_alt, f'</div>\n{reading_time}\n<div class="content-wrapper">')
    
    # 3. SNSシェアボタン（feedback-sectionの直後）
    share_buttons = create_share_buttons(article_slug)
    feedback_end = re.search(r'(<div class="feedback-section">.*?</div>)', html, re.DOTALL)
    if feedback_end:
        insert_pos = feedback_end.end()
        html = html[:insert_pos] + '\n' + share_buttons + html[insert_pos:]
    
    # 4. 関連記事（既存のnext-readを置き換え、または追加）
    related_articles = create_related_articles(article_slug)
    
    # 既存のnext-readセクションを削除
    next_read_pattern = r'<div class="next-read">.*?</div>\s*</div>'
    html = re.sub(next_read_pattern, '', html, flags=re.DOTALL)
    
    # 関連記事を</article>の直前に挿入
    html = html.replace('  </article>', f'{related_articles}\n  </article>')
    
    # ファイルに書き戻し
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ {article_slug}: features added")
    return True

def main():
    """全記事を処理"""
    blog_dir = Path('/tmp/blog-work')
    
    # 全記事ディレクトリを取得
    all_articles = []
    for cat_data in CATEGORIES.values():
        all_articles.extend(cat_data['articles'])
    
    processed = 0
    for article_slug in all_articles:
        article_dir = blog_dir / article_slug
        if article_dir.exists():
            if process_article(article_dir):
                processed += 1
    
    print(f"\n✅ Processed {processed} articles")

if __name__ == '__main__':
    main()
