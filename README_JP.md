# Star Office UI

[![EN](https://img.shields.io/badge/Lang-EN-2563eb)](README_EN.md)
[![JP](https://img.shields.io/badge/Lang-JP-e94560)](README_JP.md)
[![ZH](https://img.shields.io/badge/Lang-ZH-16a34a)](README_ZH.md)

[**English version here**](README_EN.md) | [**中文版请点击这里**](README_ZH.md)

---

マルチエージェント協調のためのピクセルオフィスダッシュボード：AIアシスタント（OpenClaw / ザリガニ）の作業状態をリアルタイムで可視化し、チームが「誰が何をしているか、昨日何をしたか、今オンラインかどうか」を直感的に確認できるようにします。

![Star Office UI プレビュー](docs/screenshots/office-preview-20260301.jpg)

---

## これは何？（一言で）

Star Office UIは「マルチ人協調ステータスダッシュボード」です。次のように考えてください：
> リアルタイム更新の「ピクセルオフィスダッシュボード」：あなたのAIアシスタント（および招待した他のエージェント）が、ステータスに応じて自動的に異なるエリア（休憩スペース / デスク / バグエリア）に移動し、昨日の作業メモも確認できます。

---

## ✨ 30秒クイックスタート（推奨）

### Docker（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/onizuka-agi-co/Star-Office-UI-JP.git
cd Star-Office-UI-JP

# Docker Composeで起動
docker compose up -d
```

アクセス：**http://localhost:18888**

### 手動インストール

```bash
# 1) リポジトリをクローン
git clone https://github.com/onizuka-agi-co/Star-Office-UI-JP.git
cd Star-Office-UI-JP

# 2) 依存関係をインストール
python3 -m pip install -r backend/requirements.txt

# 3) 状態ファイルを初期化（初回のみ）
cp state.sample.json state.json

# 4) バックエンドを起動
cd backend
python3 app.py
```

アクセス：**http://localhost:18888**

ステータスを変更してみる（プロジェクトルートから実行）：
```bash
python3 set_state.py writing "文書整理中"
python3 set_state.py syncing "同期中"
python3 set_state.py error "問題調査中"
python3 set_state.py idle "待機中"
```

---

## I. このプロジェクトの機能

Star Office UIは現在、以下を提供しています：

1. **ザリガニの作業状態を可視化**
   - ステータス：`idle`（待機）、`writing`（作業）、`researching`（調査）、`executing`（実行）、`syncing`（同期）、`error`（エラー）
   - ステータスはオフィス内の異なるエリアにマッピングされ、アニメーション/吹き出しで表示されます。

2. **「昨日のメモ」ミニサマリー**
   - UIに「昨日のメモ」カードを表示。
   - バックエンドは`memory/*.md`から昨日（または直近の利用可能な）記録を読み込み、基本的なプライバシー処理後に表示します。

3. **他のゲストをオフィスに招待（機能継続開発中）**
   - join keyで参加。
   - ゲストは自分のステータスを継続的にオフィスダッシュボードにプッシュできます。
   - 現在利用可能ですが、全体的なインタラクションとオンボーディング体験はまだ最適化中です。

4. **モバイルフレンドリーなアクセス**
   - モバイルデバイスで直接開いてステータスを確認できます（外出先でのクイックチェックに最適）。

5. **柔軟なパブリックアクセスオプション**
   - SkillはデフォルトでCloudflare Tunnelを使用してパブリックアクセスを提供します。
   - 独自のパブリックドメイン/リバースプロキシ設定も使用可能です。

6. **組み込みUI言語切り替え**
   - 英語、日本語、中国語（`EN / JP / ZH`）に対応
   - localStorage永続化による即座の言語切り替え

---

## II. このアップデートの主な変更点

このリリースでは、初期ベースバージョンと比較して以下の追加/アップグレードが行われました：

- マルチエージェントメカニズムを追加：`/join-agent`、`/agent-push`、`/leave-agent`、`/agents`
- 「昨日のメモ」エンドポイントとUIを追加：`/yesterday-memo`
- より完全なステータスシステム：`syncing`、`error`などの可視化をサポート
- シーンとキャラクターアニメーションのアップグレード：多数のピクセルアートアセットを追加（ゲストロールを含む）
- ドキュメントとSkillを書き直し：外部プログラマーにとってより初心者向けに
- リリース構造をクリーンアップ：一時ファイル/キャッシュ/ログを削除して理解のハードルを下げる
- オープンソース通知を追加：コードはMIT、ただしアートアセットは非商用
- **Dockerサポートを追加**してコンテナ化デプロイメントを実現
- **多言語UIを追加**（EN/JP/ZH言語切り替え）

---

## III. クイックスタート

### 1) 依存関係をインストール

```bash
cd star-office-ui
python3 -m pip install -r backend/requirements.txt
```

### 2) 状態ファイルを初期化

```bash
cp state.sample.json state.json
```

### 3) バックエンドを起動

```bash
cd backend
python3 app.py
```

アクセス：`http://localhost:18888`

### 4) メインエージェントのステータスを切り替え（例）

```bash
python3 set_state.py writing "文書整理中"
python3 set_state.py syncing "同期中"
python3 set_state.py error "問題調査中"
python3 set_state.py idle "待機中"
```

---

## IV. 共通API

- `GET /health`：ヘルスチェック
- `GET /status`：メインエージェントのステータス
- `POST /set_state`：メインエージェントのステータスを設定
- `GET /agents`：マルチエージェント一覧を取得
- `POST /join-agent`：ゲスト参加
- `POST /agent-push`：ゲストがステータスをプッシュ
- `POST /leave-agent`：ゲストが退出
- `GET /yesterday-memo`：昨日のメモ

---

## V. アートアセット使用上の注意（必読）

### ゲストキャラクターアセットの出典

ゲストキャラクターアニメーションはLimeZuの無料アセットを使用しています：
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

再配布/デモの際は、出典の明記と元の作者のライセンス条項に従ってください。

### その他のアセットに関する注意と免責事項（重要）

- **メインキャラクター（スターミー）と同音異義語の注記：**
  - 「スターミー」は任天堂/ポケモンの既存のキャラクターIPであり、**このプロジェクトのオリジナルではありません**。
  - このプロジェクトは**非商用のファン制作のみ**です：このキャラクターを選んだのは、「スターミー」と作者の中国語名「海辛」（Hǎi Xīn）との間に面白い同音異義語があるためです。
  - このプロジェクトのすべてのファン制作コンテンツは**学習、デモ、アイデア共有のみを目的としており、商業利用はありません**。
  - 任天堂、ポケモン、「スターミー」は任天堂/ポケモンカンパニーの商標または登録商標です。
  - このプロジェクトに関連するコンテンツを使用する予定がある場合は、独自のオリジナルキャラクター/アートアセットを使用してください。

- **オフィスシーンとその他のアセット：**プロジェクト作者チームが制作。

### 商用制限（重要）

- コード/ロジックはMITの下で使用・改変可能です。
- **このリポジトリのすべてのアートアセット（メインキャラクター/シーン/フルパックを含む）は商用利用禁止です。**
- 商用利用する場合は、独自のオリジナルアートアセットを作成して置き換えてください。

---

## VI. オープンソースライセンスと通知

- **コード/ロジック：MIT**（`LICENSE`を参照）
- **アートアセット：非商用、学習/デモのみ**

フォーク、アイデア共有、PRを歓迎しますが、アセット使用の境界を厳守してください。

---

## VII. さらなるアイデア共有を期待しています

このフレームワークを以下のように拡張してください：
- より豊富なステータスセマンティクスと自動オーケストレーション
- マルチルーム/マルチチームコラボレーションマップ
- タスクボード、タイムライン、自動生成日報
- より完全なアクセス制御と権限システム

面白い改造をしたら、ぜひ共有してください！

---

## VIII. 作者のソーシャルアカウント

- **X: Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X: Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

## プロジェクト構造（簡易版）

```text
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    join.html
    invite.html
    layout.js
    ...assets
  docs/
    screenshots/
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  README_EN.md
  README_JP.md
  README_ZH.md
  LICENSE
```
