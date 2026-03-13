import gradio as gr
import json
import os
import sys
import subprocess
from typing import List, Dict, Tuple

# Add stock-screener-master to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'stock-screener-master'))

# Theme to stocks mapping
THEME_MAPPING = {
    "aerospace": ["BA", "LMT", "NOC", "RTX", "FLY", "SPCE", "JOBY"],
    "vr": ["META", "RBLX", "NVDA", "U", "SNAP", "SONY"],
    "ar": ["AAPL", "MSFT", "GOOGL", "META", "SNAP"],
    "ai": ["NVDA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "PLTR", "AI"],
    "ev": ["TSLA", "RIVN", "NIO", "XPEV", "LI", "LCID", "FSR"],
    "crypto": ["COIN", "MSTR", "RIOT", "MARA", "HUT", "BITF"],
    "oil": ["XOM", "CVX", "COP", "EOG", "OXY", "MPC", "VLO"],
    "gold": ["NEM", "GOLD", "FNV", "WPM", "RGLD", "AUY"],
    "semiconductor": ["NVDA", "AMD", "INTC", "TSM", "QCOM", "AVGO", "MU"],
    "cloud": ["AMZN", "MSFT", "GOOGL", "CRM", "NOW", "SNOW", "DDOG"],
    "cybersecurity": ["CRWD", "PANW", "ZS", "FTNT", "OKTA", "CYBR"],
    "biotech": ["LLY", "NVO", "JNJ", "PFE", "MRK", "ABBV", "AMGN"],
    "renewable": ["ENPH", "SEDG", "FSLR", "NEE", "PLUG", "BE"],
    "fintech": ["SQ", "PYPL", "SOFI", "AFRM", "HOOD", "UPST"],
    "gaming": ["ATVI", "EA", "TTWO", "RBLX", "U", "NEXOF"],
    "space": ["SPCE", "RKLB", "ASTS", "MNTS", "JOBY"],
    "robotics": ["ISRG", "IRBT", "TER", "CGNX", "OMCL"],
}

# Event to sectors/stocks mapping
EVENT_MAPPING = {
    "iran conflict": {
        "beneficiaries": ["oil", "defense", "gold"],
        "stocks": ["XOM", "CVX", "LMT", "NOC", "RTX", "NEM", "GOLD"],
        "reason": "中东冲突推高油价，增加国防开支，避险情绪升温"
    },
    "interest rate hike": {
        "beneficiaries": ["banks", "insurance"],
        "stocks": ["JPM", "BAC", "WFC", "C", "GS", "MS", "BLK"],
        "reason": "加息扩大银行净利差，提升金融板块盈利能力"
    },
    "rate cut": {
        "beneficiaries": ["growth", "tech", "real estate"],
        "stocks": ["NVDA", "MSFT", "GOOGL", "AMZN", "META", "PLD", "AMT"],
        "reason": "降息利好高估值成长股，降低融资成本"
    },
    "china trade war": {
        "beneficiaries": ["domestic manufacturing", "agriculture"],
        "stocks": ["CAT", "DE", "ADM", "BG", "ADM"],
        "reason": "贸易战促进制造业回流，农产品出口增加"
    },
    "ai boom": {
        "beneficiaries": ["ai", "semiconductor", "cloud"],
        "stocks": ["NVDA", "AMD", "TSM", "AVGO", "MSFT", "GOOGL", "AMZN"],
        "reason": "AI浪潮推动芯片和云计算需求爆发"
    },
    "climate change": {
        "beneficiaries": ["renewable", "ev", "utilities"],
        "stocks": ["TSLA", "ENPH", "SEDG", "FSLR", "NEE", "PLUG"],
        "reason": "气候政策推动清洁能源转型"
    },
}


def get_stocks_by_theme(theme: str) -> Dict:
    """根据主题获取推荐股票"""
    theme_lower = theme.lower().strip()
    
    # Direct match
    if theme_lower in THEME_MAPPING:
        return {
            "theme": theme,
            "stocks": THEME_MAPPING[theme_lower],
            "count": len(THEME_MAPPING[theme_lower])
        }
    
    # Partial match
    matches = {}
    for key, stocks in THEME_MAPPING.items():
        if theme_lower in key or key in theme_lower:
            matches[key] = stocks
    
    if matches:
        all_stocks = []
        for stocks in matches.values():
            all_stocks.extend(stocks)
        return {
            "theme": theme,
            "matched_themes": list(matches.keys()),
            "stocks": list(set(all_stocks)),
            "count": len(set(all_stocks))
        }
    
    return {
        "theme": theme,
        "stocks": [],
        "error": f"未找到主题 '{theme}' 的相关股票，请尝试: {', '.join(list(THEME_MAPPING.keys())[:10])}..."
    }


def get_stocks_by_event(event: str) -> Dict:
    """根据事件获取推荐股票"""
    event_lower = event.lower().strip()
    
    # Check event mapping
    for key, data in EVENT_MAPPING.items():
        if key in event_lower or event_lower in key:
            return {
                "event": event,
                "matched_event": key,
                "beneficiaries": data["beneficiaries"],
                "stocks": data["stocks"],
                "reason": data["reason"],
                "count": len(data["stocks"])
            }
    
    # If no direct match, try to search with Tavily (mock for now)
    return {
        "event": event,
        "note": "未在预设事件中匹配，建议添加 Tavily API 进行新闻搜索分析",
        "stocks": ["SPY", "QQQ", "VTI"],  # Default to broad ETFs
        "reason": "无法确定具体影响，建议关注大盘ETF"
    }


def analyze_stock(ticker: str) -> str:
    """调用 stock-screener-master 分析股票"""
    try:
        # Run stock screener
        result = subprocess.run(
            ["python", "../stock-screener-master/scripts/stock_screener.py", ticker],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"分析失败: {result.stderr}"
    except Exception as e:
        return f"分析出错: {str(e)}"


def theme_recommendation(theme: str) -> str:
    """主题推荐功能"""
    result = get_stocks_by_theme(theme)
    
    if "error" in result:
        return result["error"]
    
    output = f"## 🎯 主题: {result['theme']}\n\n"
    
    if "matched_themes" in result:
        output += f"**匹配主题**: {', '.join(result['matched_themes'])}\n\n"
    
    output += f"**推荐股票** ({result['count']}只):\n\n"
    output += "| 股票代码 | 名称 | 操作 |\n"
    output += "|---------|------|------|\n"
    
    for ticker in result['stocks'][:10]:  # Limit to 10
        output += f"| {ticker} | - | [分析](#) |\n"
    
    if result['count'] > 10:
        output += f"\n*还有 {result['count'] - 10} 只股票...*\n"
    
    output += "\n---\n"
    output += "**建议**: 点击'深度分析'查看详细信息"
    
    return output


def event_recommendation(event: str) -> str:
    """事件推荐功能"""
    result = get_stocks_by_event(event)
    
    output = f"## 📰 事件: {result['event']}\n\n"
    
    if "matched_event" in result:
        output += f"**匹配事件**: {result['matched_event']}\n\n"
    
    if "beneficiaries" in result:
        output += f"**受益板块**: {', '.join(result['beneficiaries'])}\n\n"
    
    output += f"**逻辑**: {result.get('reason', 'N/A')}\n\n"
    output += f"**推荐股票** ({result.get('count', len(result['stocks']))}只):\n\n"
    output += "| 股票代码 | 预期影响 |\n"
    output += "|---------|----------|\n"
    
    for ticker in result['stocks']:
        output += f"| {ticker} | 利好 |\n"
    
    return output


def analyze_single_stock(ticker: str) -> str:
    """分析单只股票"""
    if not ticker:
        return "请输入股票代码"
    
    ticker = ticker.upper().strip()
    return analyze_stock(ticker)


# Create Gradio interface
with gr.Blocks(title="智能股票推荐系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📈 智能股票推荐系统
    
    基于主题、新闻事件和深度分析的股票推荐工具
    """)
    
    with gr.Tab("🎯 概念/主题推荐"):
        gr.Markdown("""
        输入你感兴趣的主题/概念，获取相关股票推荐
        
        **支持主题**: aerospace, vr, ai, ev, crypto, oil, gold, semiconductor, cloud, cybersecurity, biotech, renewable, fintech, gaming, space, robotics
        """)
        
        with gr.Row():
            theme_input = gr.Textbox(
                label="输入主题",
                placeholder="例如: ai, aerospace, ev...",
                value="ai"
            )
            theme_button = gr.Button("获取推荐", variant="primary")
        
        theme_output = gr.Markdown(label="推荐结果")
        theme_button.click(theme_recommendation, inputs=theme_input, outputs=theme_output)
    
    with gr.Tab("📰 新闻事件推荐"):
        gr.Markdown("""
        输入国际政治/经济事件，分析受益/受损股票
        
        **支持事件**: iran conflict, interest rate hike, rate cut, china trade war, ai boom, climate change
        """)
        
        with gr.Row():
            event_input = gr.Textbox(
                label="输入事件",
                placeholder="例如: iran conflict, rate hike...",
                value="ai boom"
            )
            event_button = gr.Button("分析事件", variant="primary")
        
        event_output = gr.Markdown(label="事件分析")
        event_button.click(event_recommendation, inputs=event_input, outputs=event_output)
    
    with gr.Tab("🔍 深度分析"):
        gr.Markdown("调用 Stock Screener Master 进行详细股票分析")
        
        with gr.Row():
            ticker_input = gr.Textbox(
                label="股票代码",
                placeholder="例如: AAPL, NVDA...",
                value="NVDA"
            )
            analyze_button = gr.Button("开始分析", variant="primary")
        
        analyze_output = gr.Textbox(
            label="分析结果",
            lines=30,
            max_lines=50
        )
        analyze_button.click(analyze_single_stock, inputs=ticker_input, outputs=analyze_output)
    
    with gr.Tab("📊 组合分析"):
        gr.Markdown("输入多个股票代码进行批量分析（用逗号分隔）")
        
        with gr.Row():
            multi_input = gr.Textbox(
                label="股票代码",
                placeholder="例如: NVDA, AMD, TSM",
                value="NVDA, AMD, TSM"
            )
            multi_button = gr.Button("批量分析", variant="primary")
        
        multi_output = gr.Textbox(
            label="分析结果",
            lines=40,
            max_lines=100
        )
        
        def analyze_multiple(tickers: str) -> str:
            ticker_list = [t.strip().upper() for t in tickers.split(",")]
            results = []
            for ticker in ticker_list[:5]:  # Limit to 5
                results.append(f"=== {ticker} ===")
                results.append(analyze_stock(ticker))
                results.append("\n" + "="*50 + "\n")
            return "\n".join(results)
        
        multi_button.click(analyze_multiple, inputs=multi_input, outputs=multi_output)

if __name__ == "__main__":
    demo.launch(share=True)
