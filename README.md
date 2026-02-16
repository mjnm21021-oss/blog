# 『AI』と暮らす『非エンジニア』の日常

OpenClaw実践記録ブログ。GitHub Pagesでホストされています。

## アクセス解析の導入手順

現在、全HTMLファイル（`index.html`, `about/index.html`, および各記事の`index.html`）の`</body>`タグ直前に、アナリティクス用のプレースホルダーコメントが挿入されています：

```html
<!-- Analytics: 解析サービス導入時にここにスクリプトを追加 -->
```

### GoatCounterを使う場合

1. https://www.goatcounter.com/ で無料アカウントを作成
2. サイト作成後、提供されるスクリプトタグをコピー
3. 全HTMLファイルのプレースホルダーコメントを以下のように置換：

```bash
# 例: GoatCounterのスクリプトタグに置換
find . -name "*.html" -type f -exec sed -i 's|<!-- Analytics: 解析サービス導入時にここにスクリプトを追加 -->|<script data-goatcounter="https://YOUR-CODE.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>|' {} \;
```

4. commit & push

### Plausible Analyticsを使う場合

1. Plausible Analytics（有料）でアカウント作成
2. サイト登録後、提供されるスクリプトタグをコピー
3. プレースホルダーコメントを置換してcommit & push

### 注意事項

- GitHub Pagesは静的サイトなので、サーバーサイドの解析は使えません
- プライバシー重視ならGoatCounterが推奨です（完全無料、軽量、GDPR準拠）
