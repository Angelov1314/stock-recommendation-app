# Stock Recommendation Web App

An intelligent stock recommendation system built with Gradio.

## Features

1. **Theme/Concept Recommendations** — Enter a theme (e.g., aerospace, VR, AI) to get related stock picks
2. **News Event Recommendations** — Enter a global event (e.g., Iran conflict) to analyze stocks that may benefit or be negatively impacted
3. **Deep Analysis** — Calls stock-screener-master for detailed analysis

## Installation

```bash
pip install gradio tavily-python yfinance pandas numpy requests python-dotenv
```

## Run

```bash
python app.py
```

## Deploy to Hugging Face

```bash
huggingface-cli login
gradio deploy
```

## Environment Variables

```bash
export TAVILY_API_KEY="your_tavily_key"
```
