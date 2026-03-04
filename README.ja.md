# Star Office UI

🌐 Language: [中文](./README.md) | [English](./README.en.md) | **日本語**

![Star Office UI カバー 2](docs/screenshots/readme-cover-2.jpg)

複数 Agent 協調向けのピクセル・オフィス可視化ダッシュボードです。AI アシスタント（OpenClaw / 「ロブスター」）の状態をリアルタイム表示し、「誰が何をしているか」「昨日何をしたか」「オンラインかどうか」を直感的に把握できます。

> このプロジェクトは **Ring Hyacinth と Simon Lee の共同制作プロジェクト（co-created project）** です。

---

## このプロジェクトは？（一言で）

Star Office UI は「複数人協調状態ダッシュボード」—— 次のように考えられます：
> リアルタイム更新の「ピクセル・オフィス・ダッシュボード」：AI アシスタント（および招待した他の Agent）は状態に応じて自動的に別のエリア（休憩室 / 作業机 / バグエリア）に移動し、昨日の作業ミニサマリーも確認できます。

---

## ✨ 30秒クイックスタート（推奨）

```bash
# 1) リポジトリをクローン
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) 依存関係をインストール
python3 -m pip install -r backend/requirements.txt

# 3) 状態ファイルを初期化（初回）
cp state.sample.json state.json

# 4) バックエンドを起動
cd backend
python3 app.py
```

開く：**http://127.0.0.1:18791**

状態を切り替えてみましょう（プロジェクトルートで実行）：
```bash
python3 set_state.py writing "ドキュメント整理中"
python3 set_state.py syncing "進捗同期中"
python3 set_state.py error "問題を検出、調査中"
python3 set_state.py idle "待機中"
```
![Star Office UI カバー 1](docs/screenshots/readme-cover-1.jpg)
---

## I. このプロジェクトが実現していること

Star Office UI は現在、次の機能を提供しています：

1. **ロブスター作業状態の可視化**
   - 状態：`idle`（待機）、`writing`（作業中）、`researching`（調査中）、`executing`（実行中）、`syncing`（同期中）、`error`（エラー）
   - 状態はオフィス内の各エリアにマッピングされ、アニメーション/吹き出しで表示されます。

2. **「昨日メモ」ミニサマリー**
   - フロントエンドに「昨日メモ」カードを表示。
   - バックエンドは `memory/*.md` から昨日（または最近利用可能な記録）を読み、簡易な匿名化を行って表示します。

3. **他ゲストの参加対応（継続改善中）**
   - join key で参加。
   - ゲストは自身の状態を継続的に push 可能。
   - 現在利用可能ですが、導線や体験は継続最適化中です。

4. **モバイル対応**
   - スマホから直接アクセスして状態確認が可能。

5. **中英日 3言語切替**
   - CN / EN / JP に対応。
   - UI 文言、読み込み文言、キャラ吹き出しが連動して切替。

6. **アートアセットのカスタマイズ**
   - サイドバーからキャラ/シーン素材を差し替え可能。
   - フレームサイズ/範囲同期によりチラつきを低減。

7. **画像生成 API 連携（背景を無限更新）**
   - 「引っ越し / 仲介探し」型の背景更新が可能。
   - 推奨モデル：`nanobanana-pro` または `nanobanana-2`。
   - API 未接続でもコア機能（状態看板/資産管理）は利用可能。

8. **公開アクセスが柔軟**
   - Cloudflare Tunnel で素早く公開可能。
   - 独自ドメイン / リバースプロキシにも対応。

---

## II. 今回のリビルド（2026-03）核心変更

今回の版は小修正ではなく、元プロジェクトに基づく全面リビルドです。主な変化は4方向：

1. **中英日 3言語追加（CN / EN / JP）**
   - 全体 UI の3言語化
   - 状態文言・提示文言・資産表示名の連動切替

2. **資産管理機能追加（全アセットのユーザー定義）**
   - サイドバーで選択・差し替え・デフォルト管理
   - キャラ・背景・装飾・ボタン等を自由に差し替え

3. **画像生成 API 接続（智能装修 + 手動装修）**
   - 「引っ越し / 仲介探し / 自分で装修」導線
   - OpenClaw で部屋スタイルを生成変更、手動テーマ入力にも対応

4. **アート資産の置換と最適化（重点）**
   - 中核資産の大規模置換・再描画
   - 命名と索引マッピングを再構築し、安定性・保守性向上
   - 動的素材の切り帧・表示ロジック最適化で誤帧/キャッシュ干渉を低減

---

## III. クイックスタート

### 1) 依存関係インストール

```bash
cd star-office-ui
python3 -m pip install -r backend/requirements.txt
```

### 2) 状態ファイル初期化

```bash
cp state.sample.json state.json
```

### 3) バックエンド起動

```bash
cd backend
python3 app.py
```

開く：`http://127.0.0.1:18791`

### 4) メイン Agent 状態切替（例）

```bash
python3 set_state.py writing "ドキュメント整理中"
python3 set_state.py syncing "進捗同期中"
python3 set_state.py error "問題を検出、調査中"
python3 set_state.py idle "待機中"
```

---

## IV. よく使う API

- `GET /health`：ヘルスチェック
- `GET /status`：メイン Agent 状態
- `POST /set_state`：メイン Agent 状態設定
- `GET /agents`：マルチ Agent リスト取得
- `POST /join-agent`：ゲスト参加
- `POST /agent-push`：ゲスト状態 push
- `POST /leave-agent`：ゲスト離脱
- `GET /yesterday-memo`：昨日メモ

---

## V. アート資産利用について（必読）

### ゲストキャラ資産の出典

LimeZu の無料素材を利用：
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

再配布/デモ時は出典表示を残し、原作者ライセンスに従ってください。

### 商用制限（重要）

- コード/ロジックは MIT で利用・改変可能。
- **本リポジトリ内の美術資産（主役/背景/素材一式）は商用不可。**
- 商用利用時は必ずオリジナル資産へ差し替えてください。

---

## VI. オープンソースライセンスと声明

- **Code / Logic：MIT**（`LICENSE` 参照）
- **Art Assets：非商用、学習/デモ用途限定**

Fork、アイデア共有、PR は歓迎。資産利用境界は厳守してください。

---

## VII. さらなる拡張へ

このフレームワークを基に、例えば：
- 状態意味の拡張と自動編排
- 多部屋/多チーム協業マップ
- タスク看板、時間線、日報自動生成
- より完備したアクセス制御・権限体系

面白い改造をしたらぜひ共有してください。

---

## VIII. プロジェクト作者

本プロジェクトは **Ring Hyacinth** と **Simon Lee** の共同制作・共同保守です。

- **X：Ring Hyacinth (@ring_hyacinth)**
  https://x.com/ring_hyacinth
- **X：Simon Lee (@simonxxoo)**
  https://x.com/simonxxoo

---

## IX. 2026-03 増分アップデート（原版に追記）

> 本節は「追加・変更点」のみを記録します。その他の構成は原版のままです。

### A) 部屋リフォーム用の画像生成モデル推奨（新規）

「引っ越し / 仲介探し」フローでは、独自の Gemini API を接続し、以下を優先することを推奨します：

1. **gemini nanobanana pro**
2. **gemini nanobanana 2**

他モデルは「部屋構造の保持 + スタイル一貫性」で期待値に届かない場合があります。

推奨設定：

- `GEMINI_API_KEY`
- `GEMINI_MODEL`（推奨：`nanobanana-pro` または `nanobanana-2`）

ランタイム設定エンドポイント：
- `GET /config/gemini`
- `POST /config/gemini`

API key が未設定の場合、サイドバーに入力入口が表示され、ユーザーがその場で入力して再試行できます。

### B) アセット編集サイドバーのパスコード（新規）

サイドバーではレイアウト・装飾・デフォルト位置を変更できます。

現在の初期値：
- `ASSET_DRAWER_PASS=1234`

推奨案内文：
1. まずはデフォルト `1234` で体験可能；
2. パスワード変更はいつでも相談可能；
3. できるだけ早く強いパスワードへ変更推奨。

例：

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

必要性：
- 公開リンクを知っている第三者によるレイアウト/素材改変を防ぐため。

### C) インストール成功後にオーナーへ伝える3点（新規）

1. **一時公開リンク**
   - `trycloudflare` の一時リンクをオーナーへ共有。
   - 後で独自ドメインへ移行できることを案内。

2. **部屋リフォーム入口**
   - 「装修房间」から開始できることを案内。
   - 初期パスワードは `1234`。
   - 変更希望があればいつでもサポート可能。
   - 強固なパスワードへの変更を推奨。

3. **画像 API 設定**
   - 画像生成にはユーザー自身の API を使用。
   - 現在は Gemini 公式 API 形式/アドレスに対応。
   - 他 API へ切替時は、先に API ドキュメント共有を依頼してから適配。

### D) 実行時ステータス運用の推奨（新規）

Agent はステータスを能動的に更新することを推奨：

1. タスク着手前に `writing / researching / executing` へ切替；
2. タスク完了後にまず `idle` へ戻してから待機。

これにより、オフィス看板上の状態がより自然で連続的に見えます。

### E) 美術・著作権表記の更新（重要）

今回の重制の重点の一つは、美術アセットシステムの刷新（大規模置換 + 命名/索引再構築）です。

維持する原則：

- コードロジック：MIT
- 美術アセット：商用不可（学習/デモ/共有用途のみ）

---


### F) 2026-03-04 P0/P1 セキュリティ・安定性アップデート（新規）

本アップデートは、**本番運用の安定性**と**状態同期の信頼性**を高めることを目的に、既存機能を維持したまま以下を実施しました。

1. **P0 セキュリティ基盤**
   - 本番モードでの安全チェックを追加（弱い secret / パスワードを拒否）
   - Session Cookie 設定を強化
   - デプロイ前検査 `scripts/security_check.py` を追加

2. **P1 構造改善（挙動変更なし）**
   - backend を `security_utils.py` / `memo_utils.py` / `store_utils.py` に分割
   - `app.py` の結合度を下げ、保守性を向上

3. **状態同期・UX 改善**
   - 状態ソース読み取り優先順位を修正
   - stale 状態の自動 `idle` 復帰を追加（偽作業中を低減）
   - 初期表示体験を改善（スケルトン表示、非重要初期化の遅延）

4. **サービス安定性修正**
   - `star-office-ui.service`（18888）の常駐動作を統一・安定化
   - `star-office-push.service` との連携を改善し、502 リスクを低減

> 詳細は `docs/UPDATE_REPORT_2026-03-04_P0_P1.md` を参照してください。

## プロジェクト構成（簡易）

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
  README.en.md
  README.ja.md
  LICENSE
```
