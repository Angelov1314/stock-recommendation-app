# Stock Recommendation Web App

基于 Gradio 的智能股票推荐系统

## 功能

1. **概念/主题推荐** - 输入主题（如 aerospace, vr, ai），推荐相关股票
2. **新闻事件推荐** - 输入国际事件（如伊朗冲突），分析受益/受损股票
3. **深度分析** - 调用 stock-screener-master 进行详细分析

## 安装

```bash
pip install gradio tavily-python yfinance pandas numpy requests python-dotenv
```

## 运行

```bash
python app.py
```

## 部署到 Hugging Face

```bash
huggingface-cli login
gradio deploy
```

## 环境变量

```bash
export TAVILY_API_KEY="your_tavily_key"
```
