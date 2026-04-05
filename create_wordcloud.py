#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import math
import random
import re
from collections import Counter
from pathlib import Path

STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "also",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "i'm",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "one",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "http",
    "https",
    "www",
    "com",
    "org",
    "net",
    "amp",
}

PALETTE = [
    "#74d7fb",
    "#ffda78",
    "#f45b82",
    "#25d7a9",
    "#f9a07a",
    "#d29bff",
    "#8ae3f5",
    "#aedf58",
    "#ffaf38",
    "#61d0f5",
    "#f47bc0",
    "#2dc3fb",
    "#a8f59a",
    "#ffd56a",
]


def build_color_sequence(count: int, seed: int) -> list[str]:
    repeats = math.ceil(count / len(PALETTE))
    colors = PALETTE * repeats
    color_rng = random.Random(seed + 1009)
    color_rng.shuffle(colors)
    return colors[:count]


def clean_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = text.replace("_", " ")
    text = re.sub(r"[^\w']+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def tokenize(text: str, min_word_length: int) -> list[str]:
    tokens = re.findall(r"[^\W\d_][\w']*", text, flags=re.UNICODE)
    return [
        token
        for token in tokens
        if len(token) >= min_word_length and token not in STOPWORDS
    ]


def estimate_box(word: str, font_size: float) -> tuple[float, float]:
    width = font_size * (0.5 * len(word) + 0.35)
    height = font_size * 0.78
    return width, height


def overlaps(rect: tuple[float, float, float, float], rects: list[tuple[float, float, float, float]]) -> bool:
    left, top, right, bottom = rect
    for other_left, other_top, other_right, other_bottom in rects:
        if right <= other_left or other_right <= left:
            continue
        if bottom <= other_top or other_bottom <= top:
            continue
        return True
    return False


def scale_font_sizes(
    frequencies: list[tuple[str, int]], min_size: int, max_size: int
) -> list[tuple[str, int, float]]:
    if not frequencies:
        return []

    counts = [count for _, count in frequencies]
    highest = max(counts)
    lowest = min(counts)

    scaled: list[tuple[str, int, float]] = []
    for word, count in frequencies:
        if highest == lowest:
            font_size = (min_size + max_size) / 2
        else:
            ratio = (
                math.log(count) - math.log(lowest)
            ) / (
                math.log(highest) - math.log(lowest)
            )
            font_size = min_size + ratio * (max_size - min_size)
        scaled.append((word, count, font_size))
    return scaled


def place_words(
    items: list[tuple[str, int, float]],
    width: int,
    height: int,
    seed: int,
) -> list[dict[str, float | str | int]]:
    rng = random.Random(seed)
    colors = build_color_sequence(len(items), seed)
    center_x = width / 2
    center_y = height / 2
    rects: list[tuple[float, float, float, float]] = []
    placed: list[dict[str, float | str | int]] = []

    for index, (word, count, font_size) in enumerate(items):
        word_width, word_height = estimate_box(word, font_size)
        padding = max(1.5, font_size * 0.04)
        start_angle = rng.random() * 2 * math.pi
        placed_word = False

        for step in range(6000):
            theta = start_angle + step * 0.33
            radius = 1.85 * math.sqrt(step + 1) * max(6.0, font_size * 0.28)
            x = center_x + math.cos(theta) * radius
            y = center_y + math.sin(theta) * radius

            rect = (
                x - word_width / 2 - padding,
                y - word_height / 2 - padding,
                x + word_width / 2 + padding,
                y + word_height / 2 + padding,
            )

            if rect[0] < 0 or rect[1] < 0 or rect[2] > width or rect[3] > height:
                continue
            if overlaps(rect, rects):
                continue

            color = colors[index]
            placed.append(
                {
                    "word": word,
                    "count": count,
                    "x": x,
                    "y": y,
                    "font_size": font_size,
                    "color": color,
                }
            )
            rects.append(rect)
            placed_word = True
            break

        if placed_word:
            continue

        for _ in range(2000):
            x = rng.uniform(word_width / 2 + padding, width - word_width / 2 - padding)
            y = rng.uniform(word_height / 2 + padding, height - word_height / 2 - padding)
            rect = (
                x - word_width / 2 - padding,
                y - word_height / 2 - padding,
                x + word_width / 2 + padding,
                y + word_height / 2 + padding,
            )
            if overlaps(rect, rects):
                continue

            color = colors[index]
            placed.append(
                {
                    "word": word,
                    "count": count,
                    "x": x,
                    "y": y,
                    "font_size": font_size,
                    "color": color,
                }
            )
            rects.append(rect)
            break

    return placed


def render_svg(
    placed_words: list[dict[str, float | str | int]],
    width: int,
    height: int,
) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#0b1118" />',
    ]

    for item in placed_words:
        word = html.escape(str(item["word"]))
        x = float(item["x"])
        y = float(item["y"])
        font_size = float(item["font_size"])
        color = str(item["color"])
        weight = 700 if font_size >= 56 else 600 if font_size >= 36 else 500
        parts.append(
            (
                f'<text x="{x:.2f}" y="{y:.2f}" '
                f'font-family="Helvetica, Arial, sans-serif" '
                f'font-size="{font_size:.2f}" font-weight="{weight}" '
                f'fill="{color}" text-anchor="middle" dominant-baseline="central">'
                f"{word}</text>"
            )
        )

    parts.append("</svg>")
    return "\n".join(parts)


def build_wordcloud(
    input_path: Path,
    output_path: Path,
    width: int,
    height: int,
    max_words: int,
    min_word_length: int,
    seed: int,
) -> int:
    raw_text = input_path.read_text(encoding="utf-8", errors="ignore")
    cleaned_text = clean_text(raw_text)
    tokens = tokenize(cleaned_text, min_word_length=min_word_length)

    if not tokens:
        raise ValueError("No words found after filtering.")

    frequencies = Counter(tokens).most_common(max_words)
    sized_words = scale_font_sizes(frequencies, min_size=9, max_size=70)
    placed_words = place_words(sized_words, width=width, height=height, seed=seed)

    if not placed_words:
        raise ValueError("Could not place any words on the canvas.")

    svg = render_svg(placed_words, width=width, height=height)
    output_path.write_text(svg, encoding="utf-8")
    return len(placed_words)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a word cloud SVG from a text file."
    )
    parser.add_argument(
        "--input",
        default="output.txt",
        help="Input text file path. Defaults to output.txt.",
    )
    parser.add_argument(
        "--output",
        default="output_wordcloud.svg",
        help="Output SVG path. Defaults to output_wordcloud.svg.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1600,
        help="Canvas width in pixels. Defaults to 1600.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=900,
        help="Canvas height in pixels. Defaults to 900.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=320,
        help="Maximum number of words to place. Defaults to 320.",
    )
    parser.add_argument(
        "--min-word-length",
        type=int,
        default=2,
        help="Minimum word length after cleaning. Defaults to 2.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for reproducible layout. Defaults to 7.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        print(f"Input file not found: {input_path}")
        return 1

    try:
        placed_count = build_wordcloud(
            input_path=input_path,
            output_path=output_path,
            width=args.width,
            height=args.height,
            max_words=args.max_words,
            min_word_length=args.min_word_length,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Saved word cloud to {output_path} with {placed_count} placed words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
