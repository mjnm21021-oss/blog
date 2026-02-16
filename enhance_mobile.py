#!/usr/bin/env python3
"""
ブログ記事にモバイル読み体験改善機能を追加するスクリプト
"""
import os
import re
from pathlib import Path

# 追加するCSS
TOC_CSS = """
  /* 目次 (TOC) */
  .toc {
    background: #f9f9f9;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 24px 0 36px;
  }
  .toc-title {
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 12px;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .toc-title::before { content: '📑'; }
  .toc-title::after { content: '▼'; font-size: 11px; color: #999; transition: transform 0.3s; }
  .toc.collapsed .toc-title::after { transform: rotate(-90deg); }
  .toc ol {
    margin: 0;
    padding-left: 20px;
    counter-reset: toc-counter;
    list-style: none;
  }
  .toc li {
    counter-increment: toc-counter;
    margin: 8px 0;
    font-size: 14px;
    line-height: 1.6;
  }
  .toc li::before {
    content: counter(toc-counter) '. ';
    color: #e63946;
    font-weight: 700;
  }
  .toc a { color: #1a1a1a; text-decoration: none; }
  .toc a:hover { color: #e63946; }
  .toc.collapsed ol { display: none; }
"""

PROGRESS_BAR_CSS = """
  /* 読了プログレスバー */
  .progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: #e63946;
    z-index: 9999;
    transition: width 0.1s linear;
    width: 0%;
  }
"""

SECTION_NUMBER_CSS = """
  /* h2セクション番号 */
  article { counter-reset: section-counter; }
  article h2 { counter-increment: section-counter; }
  article h2::before {
    content: counter(section-counter, decimal-leading-zero) ' ';
    display: inline-block;
    color: #e63946;
    font-size: 14px;
    font-weight: 700;
    margin-right: 12px;
    opacity: 0.7;
  }
"""

BACK_TO_TOP_CSS = """
  /* トップに戻るボタン */
  .back-to-top {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 44px;
    height: 44px;
    background: #e63946;
    color: #fff;
    border: none;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  .back-to-top.visible { opacity: 1; }
  .back-to-top:hover { background: #c5303c; }
"""

# 追加するJavaScript
MOBILE_ENHANCEMENTS_JS = """
<script>
// TOC 折りたたみ
document.querySelectorAll('.toc-title').forEach(t => {
  t.addEventListener('click', () => t.parentElement.classList.toggle('collapsed'));
});

// 読了プログレスバー
window.addEventListener('scroll', function() {
  var h = document.documentElement;
  var progress = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
  document.getElementById('progressBar').style.width = progress + '%';
});

// トップに戻るボタン
var btn = document.getElementById('backToTop');
window.addEventListener('scroll', function() {
  btn.classList.toggle('visible', window.scrollY > 500);
});
btn.addEventListener('click', function() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
</script>
"""

def extract_h2_headings(html_content):
    """記事からh2見出しを抽出"""
    # article内のh2を探す（サイドバーのh2は除外）
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html_content, re.DOTALL)
    if not article_match:
        return []
    
    article_content = article_match.group(1)
    h2_pattern = r'<h2[^>]*>(.*?)</h2>'
    headings = re.findall(h2_pattern, article_content)
    
    # HTMLタグを除去
    clean_headings = []
    for h in headings:
        clean = re.sub(r'<[^>]+>', '', h)
        clean_headings.append(clean.strip())
    
    return clean_headings

def generate_toc_html(headings):
    """目次HTMLを生成"""
    if not headings:
        return ""
    
    toc_items = []
    for i, heading in enumerate(headings, 1):
        toc_items.append(f'      <li><a href="#sec-{i}">{heading}</a></li>')
    
    toc_html = f"""
    <!-- 目次 -->
    <div class="toc">
      <div class="toc-title">目次</div>
      <ol>
{chr(10).join(toc_items)}
      </ol>
    </div>
"""
    return toc_html

def add_h2_ids(html_content):
    """h2にid属性を追加"""
    counter = [0]  # クロージャで使うためリストにする
    
    def replace_h2(match):
        counter[0] += 1
        tag = match.group(0)
        # 既にidがある場合はスキップ
        if 'id=' in tag:
            return tag
        # article内のh2のみカウント
        if counter[0] <= 50:  # 安全のため上限設定
            return tag.replace('<h2', f'<h2 id="sec-{counter[0]}"')
        return tag
    
    # article内のh2を処理
    def process_article(match):
        article_content = match.group(1)
        counter[0] = 0
        modified = re.sub(r'<h2[^>]*>', replace_h2, article_content)
        return f'<article{match.group(0)[8:match.start(1)-match.start(0)]}{modified}</article>'
    
    result = re.sub(r'<article[^>]*>(.*?)</article>', process_article, html_content, flags=re.DOTALL)
    return result

def enhance_article(html_path, add_toc=True):
    """記事ファイルを拡張"""
    print(f"Processing: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 既に処理済みかチェック（JavaScriptまで追加されているか）
    if 'progress-bar' in content and 'back-to-top' in content and 'var btn = document.getElementById(\'backToTop\')' in content:
        print(f"  → Already enhanced, skipping")
        return
    
    # 1. CSSを追加（</style>の前に）
    if 'toc {' not in content:
        content = content.replace('</style>', f'{TOC_CSS}\n{PROGRESS_BAR_CSS}\n{SECTION_NUMBER_CSS}\n{BACK_TO_TOP_CSS}\n</style>')
    
    # 2. プログレスバーを<body>直後に追加
    if '<div class="progress-bar"' not in content:
        content = content.replace('<body>', '<body>\n<div class="progress-bar" id="progressBar"></div>')
    
    # 3. h2にid属性を追加
    content = add_h2_ids(content)
    
    # 4. TOCを追加（aboutは除外）
    if add_toc and '<div class="toc">' not in content:
        headings = extract_h2_headings(content)
        if headings:
            toc_html = generate_toc_html(headings)
            # article-headerの直後に挿入（</div>の後、最初のh2の前）
            # より確実に: article-headerを含むdivの閉じタグの後
            pattern = r'(</dl>\s*</div>\s*)((?:\s*<hr[^>]*>)?\s*)(<h2)'
            if re.search(pattern, content):
                content = re.sub(pattern, rf'\1{toc_html}\2\3', content, count=1)
            else:
                # フォールバック: 最初のh2の直前
                content = re.sub(r'(<h2[^>]*id="sec-1")', rf'{toc_html}\n    \1', content, count=1)
    
    # 5. トップに戻るボタンを</body>の前に追加
    if '<button class="back-to-top"' not in content:
        content = content.replace('</body>', '<button class="back-to-top" id="backToTop">↑</button>\n</body>')
    
    # 6. JavaScriptを追加（</body>の前、back-to-topボタンの前に）
    if 'var btn = document.getElementById(\'backToTop\')' not in content:
        # back-to-topボタンの直前に挿入
        content = content.replace('<button class="back-to-top"', f'{MOBILE_ENHANCEMENTS_JS}\n<button class="back-to-top"')
    
    # ファイルに書き戻し
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Enhanced")

def main():
    blog_dir = Path('/tmp/blog-work')
    
    # 対象ディレクトリ
    article_dirs = [
        'about',
        'backtest-failures', 
        'backtest-method',
        'backtest-overview',
        'comfyui',
        'cron-heartbeat',
        'day1',
        'morning-briefing',
        'multi-agent-flow',
        'soul-md-merged',
        'token-efficiency'
    ]
    
    for dir_name in article_dirs:
        html_file = blog_dir / dir_name / 'index.html'
        if html_file.exists():
            # aboutはTOC不要
            add_toc = (dir_name != 'about')
            enhance_article(html_file, add_toc=add_toc)
        else:
            print(f"Warning: {html_file} not found")
    
    # index.html（ホーム）も処理（TOC不要）
    index_file = blog_dir / 'index.html'
    if index_file.exists():
        print(f"\nProcessing home page: {index_file}")
        enhance_article(index_file, add_toc=False)
    
    print("\n✓ All articles enhanced!")

if __name__ == '__main__':
    main()
