# Gemini 論文要約ツール

PDFの論文を読み込み、Gemini APIを使用して論文の内容を日本語で要約・翻訳するツールです。

## 機能

- PDFファイルからテキストを抽出
- Gemini APIを使用した論文の要約生成
- 論文の翻訳
- 処理ログの自動保存
- マークダウンからPDFへの変換
- 料金計算と使用統計の表示

## インストール方法

### 前提条件

- Python 3.10以上
- Google AI Studio APIキー
- Pandoc（マークダウンからPDFへの変換に必要）
- LaTeX（PDFレンダリングに必要）

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/gemini-paper-summarizer.git
cd gemini-paper-summarizer
```

2. 仮想環境を作成して有効化

```bash
python -m venv .venv
source .venv/bin/activate  # Linuxの場合
# または
.venv\Scripts\activate.bat  # Windowsの場合
```

3. 依存パッケージをインストール

このプロジェクトは[uv](https://github.com/astral-sh/uv)を使用してパッケージ管理を行っています。

```bash
# uvがインストールされている場合
uv pip install -e .

# pipを使用する場合
pip install -e .
```

4. `.env`ファイルを作成し、APIキーを設定

```bash
echo "GEMINI_API_KEY=あなたのAPIキー" > .env
```

5. Pandocと必要なLaTeXパッケージをインストール

```bash
# Debian/Ubuntuの場合
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended texlive-lang-japanese
```

## 使用方法

### 基本的な使い方

単一のPDFファイルを処理：

```bash
gp-summarize path/to/paper.pdf
```

ディレクトリ内のすべてのPDFファイルを処理：

```bash
gp-summarize path/to/directory/
```


### オプション

```
usage: gp-summarize [-h] [--output OUTPUT] [--output-dir OUTPUT_DIR] [--suffix SUFFIX] 
                   [--model MODEL] [--temperature TEMPERATURE] [--top-p TOP_P] 
                   [--top-k TOP_K] [--max-output-tokens MAX_OUTPUT_TOKENS] 
                   [--rpm RPM] [--ccache] [--convert-pdf] [--nosummary] [--version]
                   input

論文PDFをGeminiで要約・翻訳するツール

positional arguments:
  input                 入力PDFファイルまたはディレクトリのパス

options:
  -h, --help            ヘルプメッセージを表示して終了
  --output OUTPUT       出力先ファイル名（デフォルト: 入力ファイル名に基づく）
  --output-dir OUTPUT_DIR
                        出力先ディレクトリ
  --suffix SUFFIX       出力ファイル名に追加する接尾辞
  --model MODEL         使用するGeminiモデル名 (デフォルト: gemini-1.5-pro)
  --temperature TEMPERATURE
                        生成時の温度パラメータ (デフォルト: 0.4)
  --top-p TOP_P         生成時のtop-pパラメータ (デフォルト: 1.0)
  --top-k TOP_K         生成時のtop-kパラメータ (デフォルト: 32)
  --max-output-tokens MAX_OUTPUT_TOKENS
                        最大出力トークン数 (デフォルト: 8192)
  --rpm RPM             1分あたりの最大リクエスト数 (デフォルト: 2)
  --ccache              コンテンツキャッシュを使用する
  --convert-pdf         生成されたマークダウンをPDFに変換する
  --nosummary           要約生成をスキップする
  --version             バージョン情報を表示して終了
```

### マークダウンからPDFへの変換（スタンドアロンツール）

マークダウンファイルをPDFに変換するだけなら、専用のツールも用意されています：

```bash
md-to-pdf path/to/file.md
```

ディレクトリ内のすべてのマークダウンファイルを変換：

```bash
md-to-pdf path/to/directory/ -r
```

オプション：

```
usage: md-to-pdf [-h] [-o OUTPUT] [-r] [-f FONT] input

マークダウンファイルをPDFに変換するツール

positional arguments:
  input                 入力マークダウンファイルまたはディレクトリ

options:
  -h, --help            ヘルプメッセージを表示して終了
  -o, --output OUTPUT   出力PDFファイルまたはディレクトリ
  -r, --recursive       ディレクトリ内を再帰的に検索
  -f, --font FONT       PDFで使用するフォント名 (デフォルト: IPAexGothic)
```

## 依存パッケージ

このツールは以下の主要なパッケージに依存しています：

- `google-genai` / `google-generativeai` - Gemini APIとの通信
- `marker-pdf` - PDFからテキストを抽出
- `pypandoc` - マークダウンからPDFへの変換
- `python-dotenv` - 環境変数の管理

## パッケージ管理

このプロジェクトでは、[uv](https://github.com/astral-sh/uv)を使用してパッケージ管理を行っています。uvはPythonのパッケージインストールと環境管理のための高速なツールで、依存関係の解決を効率的に行います。

パッケージの追加や更新を行う場合は、以下のコマンドを使用します：

```bash
# パッケージのインストール
uv pip install パッケージ名

# 開発環境へのインストール
uv pip install -e .
```

`uv.lock`ファイルには、すべての依存関係の正確なバージョンが記録されており、環境の再現性を確保しています。


## 注意事項

- Gemini APIの利用には制限があります。RPMオプションを適切に設定してください。
- 大きなPDFファイルは処理に時間がかかる場合があります。
- PDF変換には、pandocとLaTeXの環境が必要です。
- 日本語PDF出力には、IPAexGothicなどの日本語フォントが必要です。
- PDF出力で画像を表示するには、マークダウン内で相対パスまたは絶対パスで画像を参照してください。
