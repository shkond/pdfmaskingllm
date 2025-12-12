import os
from pathlib import Path

from pdfminer.high_level import extract_text as extract_pdf_text
import docx  # python-docx

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


MODEL_NAME = "tokyotech-llm/Gemma-2-Llama-Swallow-9b-it-v0.1"


def load_model(device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
    )
    return tokenizer, model


SYSTEM_PROMPT = """あなたは個人情報マスキング用のアシスタントです。
次の制約を厳密に守ってください。
- 入力は履歴書のテキストです。日本語と英語が混在している場合があります。
- 氏名・住所・電話番号・メールアドレス・生年月日・郵便番号を [[MASK]] に置き換えてください。
- それ以外のテキスト（職務内容の説明、スキル、自己PR、学歴など）は、一切変更せずにそのまま出力してください。
- 改行や段落構造も極力そのまま維持してください。
- 出力は「マスク済みテキストのみ」を返し、説明やコメントは一切書かないでください。
"""

USER_PROMPT_TEMPLATE = """以下の履歴書テキスト中の個人情報を [[MASK]] に置き換えてください。

<<<RESUME_TEXT_START>>>
{resume_text}
<<<RESUME_TEXT_END>>>"""


def mask_pii_with_llm(text: str, tokenizer, model, device: str = "cuda") -> str:
    user_prompt = USER_PROMPT_TEMPLATE.format(resume_text=text)
    full_prompt = f"<system>\n{SYSTEM_PROMPT}\n</system>\n<user>\n{user_prompt}\n</user>\n"

    inputs = tokenizer(
        full_prompt,
        return_tensors="pt",
        truncation=True,
        max_length=4096,
    ).to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            do_sample=False,
        )

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # プロンプト部分を削る簡易処理
    if full_prompt in output_text:
        masked = output_text.split(full_prompt, 1)[1].lstrip()
    else:
        masked = output_text

    return masked


def extract_text_from_pdf(path: Path) -> str:
    return extract_pdf_text(str(path))


def extract_text_from_docx(path: Path) -> str:
    doc = docx.Document(str(path))
    lines = [p.text for p in doc.paragraphs]
    return "\n".join(lines)


def main():
    root = Path(".").resolve()
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer, model = load_model(device=device)
    #model.to(device)

    # ルート直下のPDFとDOCXを列挙
    targets = list(root.glob("*.pdf")) + list(root.glob("*.docx"))

    for path in targets:
        print(f"processing: {path.name}")

        if path.suffix.lower() == ".pdf":
            text = extract_text_from_pdf(path)
        elif path.suffix.lower() == ".docx":
            text = extract_text_from_docx(path)
        else:
            continue

        masked = mask_pii_with_llm(text, tokenizer, model, device=device)

        out_name = f"{path.name}.txt"  # 例: sample.pdf -> sample.pdf.txt
        out_path = output_dir / out_name

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(masked)

    print("done.")


if __name__ == "__main__":
    main()
