from flask import Flask, render_template, request, jsonify
import json
import sys
import os
import subprocess

app = Flask(__name__)

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
    "5g": ["T", "VZ", "TMUS", "ERIC", "NOK", "QCOM"],
    "基因编辑": ["CRSP", "EDIT", "NTLA", "BEAM", "VRTX"],
    "量子计算": ["IBM", "GOOGL", "MSFT", "IONQ", "RGTI"],
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/themes')
def get_themes():
    return jsonify(list(THEME_MAPPING.keys()))

@app.route('/api/theme/<theme>')
def get_theme_stocks(theme):
    theme_lower = theme.lower().strip()
    
    if theme_lower in THEME_MAPPING:
        return jsonify({
            "theme": theme,
            "stocks": THEME_MAPPING[theme_lower],
            "count": len(THEME_MAPPING[theme_lower])
        })
    
    # Partial match
    matches = {}
    for key, stocks in THEME_MAPPING.items():
        if theme_lower in key or key in theme_lower:
            matches[key] = stocks
    
    if matches:
        all_stocks = []
        for stocks in matches.values():
            all_stocks.extend(stocks)
        return jsonify({
            "theme": theme,
            "matched_themes": list(matches.keys()),
            "stocks": list(set(all_stocks)),
            "count": len(set(all_stocks))
        })
    
    return jsonify({"error": "Theme not found"}), 404

@app.route('/api/event/<event>')
def get_event_stocks(event):
    event_lower = event.lower().strip()
    
    for key, data in EVENT_MAPPING.items():
        if key in event_lower or event_lower in key:
            return jsonify({
                "event": event,
                "matched_event": key,
                "beneficiaries": data["beneficiaries"],
                "stocks": data["stocks"],
                "reason": data["reason"]
            })
    
    return jsonify({
        "event": event,
        "note": "Event not in preset list, using broad ETFs as default",
        "stocks": ["SPY", "QQQ", "VTI"],
        "reason": "Unable to determine specific impact, focus on broad market ETFs"
    })

@app.route('/api/analyze/<ticker>')
def analyze_stock(ticker):
    try:
        result = subprocess.run(
            ["python3", "../stock-screener-master/scripts/stock_screener.py", ticker.upper()],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            return jsonify({"ticker": ticker.upper(), "analysis": result.stdout})
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=7860)
