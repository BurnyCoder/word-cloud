# Word Cloud Generator

Small Python script that turns a text file into a word cloud SVG without any third-party dependencies.

## Features

- Pure standard-library Python
- Cleans markdown-style text and URLs before tokenizing
- Filters common stopwords
- Produces reproducible layouts with a configurable random seed
- Writes scalable SVG output

## Usage

```bash
python create_wordcloud.py --input output.txt --output output_wordcloud.svg
```

### Common options

```bash
python create_wordcloud.py \
  --input output.txt \
  --output output_wordcloud.svg \
  --width 1600 \
  --height 900 \
  --max-words 320 \
  --min-word-length 2 \
  --seed 7
```

## Example Output

The script writes SVG. The preview below is an exported PNG example generated from the same word cloud output.

![Example word cloud](output_wordcloud.png)

## Requirements

- Python 3.10+

## Files

- `create_wordcloud.py`: main script
- `output_wordcloud.png`: example image shown above
