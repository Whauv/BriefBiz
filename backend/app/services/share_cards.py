from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

from app.models.article import Article

CARD_SIZE = (1080, 1080)


class ShareCardService:
    def __init__(self) -> None:
        self.output_dir = Path(__file__).resolve().parents[2] / "media" / "share-cards"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_card(self, article: Article) -> Path:
        image = Image.new("RGB", CARD_SIZE, self._background(article.sentiment.value))
        draw = ImageDraw.Draw(image)
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

        self._draw_gradient_overlay(draw)
        draw.text((72, 56), "BRIEFBIZ", font=label_font, fill=(240, 248, 255))
        draw.text((72, 94), "Business news, distilled", font=body_font, fill=(216, 226, 255))

        title_lines = "\n".join(wrap(article.title, width=28))
        summary_lines = "\n".join(wrap(article.summary_60w or "", width=42))
        draw.multiline_text((72, 260), title_lines, font=title_font, fill=(255, 255, 255), spacing=14)
        draw.multiline_text((72, 560), summary_lines, font=body_font, fill=(231, 235, 255), spacing=12)

        footer = f"{article.source_name}  •  {article.sentiment.value.upper()}"
        draw.rounded_rectangle((660, 940, 1008, 1000), radius=28, fill=(15, 23, 42))
        draw.text((690, 958), footer, font=label_font, fill=(255, 255, 255))

        output_path = self.output_dir / f"article-{article.id}.png"
        image.save(output_path, format="PNG")
        return output_path

    def _background(self, sentiment: str) -> tuple[int, int, int]:
        return {
            "bullish": (16, 74, 56),
            "bearish": (104, 33, 52),
            "risk": (122, 70, 18),
            "neutral": (24, 39, 68),
        }.get(sentiment, (24, 39, 68))

    def _draw_gradient_overlay(self, draw: ImageDraw.ImageDraw) -> None:
        for step in range(0, CARD_SIZE[1], 4):
            alpha = int(80 * (step / CARD_SIZE[1]))
            draw.line((0, step, CARD_SIZE[0], step), fill=(3 + alpha, 7 + alpha, 18 + alpha), width=4)
