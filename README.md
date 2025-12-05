以下のような `README.md` にしておくとよいです。

***

# 履歴書マスキングCLI

PDF / Word（.docx）の履歴書からテキストを抽出し、ローカルLLM  
`tokyotech-llm/Gemma-2-Llama-Swallow-9b-it-v0.1` を使って個人情報を `[[MASK]]` に置き換えた `.txt` を出力するCLIツールです。[1]

## 前提環境

- Python 3.10 以上を推奨  
- GPU がある場合は CUDA 対応版 PyTorch を入れると高速になります  
- 仮想環境（venv / conda など）の利用を推奨  

## 仮想環境の作成・有効化（例）

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

以降の `pip install` は、この仮想環境の中で実行する想定です。  
（グローバル環境に入れたい場合は、このステップは省略可）

## 必要ライブラリのインストール

### 1. PyTorch のインストール

GPU / CUDA の有無によってコマンドが変わるため、公式サイトで自分の環境に合うコマンドを確認してください。[2]

- PyTorch 公式: https://pytorch.org/get-started/locally/  

例（CPU版でよい場合）:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 2. その他ライブラリを requirements.txt からインストール

このリポジトリのルートにある `requirements.txt` には、以下のようなパッケージが含まれています。[3][4]

```txt
transformers
accelerate
pdfminer.six
python-docx
```

インストールコマンド:

```bash
pip install -r requirements.txt
```

> 補足:  
> 「Defaulting to user installation because normal site-packages is not writeable」と表示される場合、  
> - グローバル環境に書き込み権限がないため、ユーザー領域にインストールされています。  
> - 仮想環境を使う場合は、上記の venv を有効化した上で再度 `pip install -r requirements.txt` を実行してください。[5][6]

## モデルのダウンロードについて

`tokyotech-llm/Gemma-2-Llama-Swallow-9b-it-v0.1` は Hugging Face から取得します。[1]

初回実行時に自動でダウンロードされますが、事前に `huggingface-cli login` などで認証を通しておく必要がある場合があります。[7]

```bash
pip install "huggingface_hub[cli]"
huggingface-cli login
```

## 使い方

1. ルートディレクトリに、マスクしたい `*.pdf` / `*.docx` を配置する  
2. `mask_resume_llm.py` もルートに置く  
3. 仮想環境を有効化（任意）  
4. 以下のコマンドを実行

```bash
python mask_resume_llm.py
```

- ルート直下の `*.pdf` / `*.docx` を自動で検出  
- `output/` ディレクトリを作成  
- 各ファイルに対し、`output/元ファイル名.pdf.txt` / `output/元ファイル名.docx.txt` を出力します。[8][9]

## トラブルシューティング

- `Defaulting to user installation ...` が出る  
  - 管理者権限のないグローバル環境にインストールしようとしているメッセージです。  
  - 仮想環境を作成し、有効化した状態で `pip install -r requirements.txt` を実行してください。[6][5]

- モデルロードでメモリ不足になる  
  - GPUメモリが少ない場合は CPU 実行に切り替えるか、量子化版モデル・より小さいモデルへの変更を検討してください。[7]

---
