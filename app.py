import re
from decimal import Decimal, ROUND_HALF_UP

import streamlit as st
from PIL import Image
import pytesseract


def round_half_up(value: float, ndigits: int = 1) -> float:
    q = Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))


def mm_to_cm_1dp(mm_value: float) -> float:
    return round_half_up(mm_value / 10.0, 1)


def extract_wh_mm(img: Image.Image):
    config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(img, config=config)

    w_match = re.search(r"\bW\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*mm\b", text, re.IGNORECASE)
    h_match = re.search(r"\bH\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*mm\b", text, re.IGNORECASE)

    if not w_match:
        w_match = re.search(r"\bW\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)
    if not h_match:
        h_match = re.search(r"\bH\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\b", text, re.IGNORECASE)

    if not w_match or not h_match:
        return None, text

    w_mm = float(w_match.group(1))
    h_mm = float(h_match.group(1))
    return (w_mm, h_mm), text


st.set_page_config(page_title="W/H 読み取り → cm変換", page_icon="📐")
st.title("📐 スクショから W / H を読み取り → cm に変換")

uploaded = st.file_uploader("スクリーンショット画像をアップロード（PNG/JPGなど）", type=["png", "jpg", "jpeg", "webp", "bmp"])
show_ocr = st.checkbox("デバッグ：OCRの生テキストを表示", value=False)

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="アップロード画像", use_container_width=True)

    result, ocr_text = extract_wh_mm(img)

    if result is None:
        st.error("W/H の数値を見つけられませんでした。別の画像で試すか、W/H周辺がはっきり写るスクショにしてください。")
        if show_ocr:
            st.subheader("OCRテキスト")
            st.code(ocr_text)
    else:
        w_mm, h_mm = result
        w_cm = mm_to_cm_1dp(w_mm)
        h_cm = mm_to_cm_1dp(h_mm)

        output = f"タテ(H) 約 {h_cm:.1f} cm\nヨコ(W) 約 {w_cm:.1f} cm"

        st.success("読み取り成功")
        st.text_area("出力（コピーして使えます）", value=output, height=100)

        if show_ocr:
            st.subheader("OCRテキスト")
            st.code(ocr_text)
