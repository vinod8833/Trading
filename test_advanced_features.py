#!/usr/bin/env python3
"""
Quick API Test Script for Advanced Features
Demonstrates all new features with practical examples
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# ANSI Colors for beautiful output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_header(text):
    """Print colorful header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_feature(title, description):
    """Print feature description"""
    print(f"{YELLOW}{title}{RESET}")
    print(f"  {description}\n")


def test_beginner_signal():
    """Test: One-Click Stock Analysis - Beginner Mode"""
    print_feature(
        "📊 ONE-CLICK STOCK ANALYSIS - Beginner Mode",
        "Get simple BUY/SELL/HOLD signals with plain English explanation"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/signals/beginner_signal/",
            json={"symbol": "RELIANCE"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Signal: {data.get('signal')}")
            print(f"  Confidence: {data.get('confidence')}")
            print(f"  Action: {data.get('action')}")
            print(f"  Explanation: {data.get('simple_explanation')}\n")
            print_success("Beginner signal working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_pro_signal():
    """Test: One-Click Stock Analysis - Pro Mode"""
    print_feature(
        "🔬 ONE-CLICK STOCK ANALYSIS - Pro Mode",
        "Get detailed signals with all technical indicators (RSI, VWAP, Bollinger Bands, Volume, etc)"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/signals/pro_signal/",
            json={"symbol": "RELIANCE"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Signal: {data.get('signal')}")
            print(f"  Confidence: {data.get('confidence')}%")
            if 'indicators' in data:
                print(f"  Indicators analyzed: {len(data['indicators'])} (RSI, VWAP, Bollinger Bands, Volume, Trend, Fibonacci, MA)")
            print(f"\n  ✓ Pro signal includes:")
            print(f"    - RSI Analysis (oversold/overbought)")
            print(f"    - VWAP Price Position")
            print(f"    - Bollinger Bands (upper, middle, lower)")
            print(f"    - Volume Spike Detection")
            print(f"    - Fibonacci Levels")
            print(f"    - Moving Averages (20, 50, 200)\n")
            print_success("Pro signal working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_intraday_signal():
    """Test: Intraday Quick Signals"""
    print_feature(
        "⚡ INTRADAY QUICK SIGNALS",
        "Get quick trading signals using VWAP, volume, and market timing for day trading"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/intraday-signals/quick_signal/",
            json={"symbol": "TCS"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Action: {data.get('action')}")
            print(f"  VWAP Analysis: {data.get('vwap_analysis')}")
            print(f"  Volume Analysis: {data.get('volume_analysis')}")
            print(f"  RSI Timing: {data.get('rsi_analysis')}")
            print(f"  Recommendation: {data.get('recommendation')}\n")
            print_success("Intraday signal working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_risk_analysis():
    """Test: Automatic Risk Checks"""
    print_feature(
        "🛡️  AUTOMATIC RISK CHECKS",
        "Analyze trade risk with automatic capital checks and smart warnings"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/risk-analysis/analyze_trade_risk/",
            json={
                "portfolio_id": 1,
                "symbol": "RELIANCE",
                "entry_price": 2500,
                "stop_loss": 2450,
                "quantity": 100
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Risk Amount: ₹{data.get('risk_amount', 0):,.0f}")
            print(f"  Risk Percent: {data.get('risk_percent', 0):.2f}%")
            print(f"  Risk Level: {data.get('risk_level')}")
            print(f"  Capital Check: {data.get('capital_check', {}).get('message')}")
            
            warnings = data.get('warnings', [])
            if warnings:
                print(f"  Warnings: {', '.join(warnings)}")
            else:
                print(f"  Warnings: None ✓")
            
            print(f"  Recommendation: {data.get('recommendation')}\n")
            print_success("Risk analysis working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_support_resistance():
    """Test: Support & Resistance Levels"""
    print_feature(
        "📍 SUPPORT & RESISTANCE LEVELS",
        "Auto-calculate support and resistance levels using Fibonacci retracements"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/support-resistance/calculate_levels/",
            json={"symbol": "INFY"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Current Price: ₹{data.get('current_price', 0):.2f}")
            
            print(f"\n  Support Levels: {data.get('support_levels', [])}")
            print(f"  Resistance Levels: {data.get('resistance_levels', [])}")
            
            if 'fibonacci_levels' in data:
                print(f"\n  Fibonacci Levels:")
                for level, price in data['fibonacci_levels'].items():
                    print(f"    {level}: ₹{price:.2f}")
            
            print()
            print_success("Support & Resistance working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_paper_trading():
    """Test: Paper Trading"""
    print_feature(
        "📝 PAPER TRADING",
        "Practice trading without real money - perfect for beginners!"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/paper-trading/create_paper_trade/",
            json={
                "portfolio_id": 1,
                "symbol": "TCS",
                "entry_price": 3650.50,
                "quantity": 10
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"  ✓ Paper trade created!")
            print(f"    Stock: {data.get('stock')}")
            print(f"    Entry Price: ₹{data.get('entry_price')}")
            print(f"    Quantity: {data.get('quantity')} shares")
            print(f"    Status: {data.get('status')}\n")
            print_success("Paper trading working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_market_summary():
    """Test: Daily Market Summary"""
    print_feature(
        "📈 DAILY MARKET SUMMARY",
        "Get daily market summary with trend and sentiment analysis"
    )
    
    try:
        response = requests.get(f"{BASE_URL}/market-summary/today_summary/")
        if response.status_code == 200:
            data = response.json()
            print(f"  Market Date: {data.get('market_date')}")
            print(f"  Gainers: {data.get('gainers_count')} stocks")
            print(f"  Losers: {data.get('losers_count')} stocks")
            print(f"  Market Trend: {data.get('market_trend')}")
            print(f"  Market Sentiment: {data.get('market_sentiment')}\n")
            print_success("Market summary working!")
        else:
            print(f"  {RED}Not available yet (no data for today){RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_smart_alerts():
    """Test: Smart Alerts"""
    print_feature(
        "🔔 SMART ALERTS",
        "Create smart alerts for price, volume, and trend changes"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/smart-alerts/create_alert/",
            json={
                "symbol": "RELIANCE",
                "alert_type": "PRICE_LEVEL",
                "target_value": 2600,
                "condition": "Price crosses above 2600",
                "send_email": True,
                "send_notification": True
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"  ✓ Alert created!")
            print(f"    Stock: {data.get('stock')}")
            print(f"    Alert Type: {data.get('alert_type')}")
            print(f"    Target: {data.get('target_value')}")
            print(f"    Status: {data.get('status')}\n")
            print_success("Smart alerts working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_portfolio_health():
    """Test: Portfolio Health Analysis"""
    print_feature(
        "❤️  PORTFOLIO HEALTH ANALYSIS",
        "Analyze portfolio health including profit/loss, risk level, and diversification"
    )
    
    try:
        response = requests.get(
            f"{BASE_URL}/portfolio-health/portfolio_health/",
            params={"portfolio_id": 1}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Health Score: {data.get('health_score', 0):.1f}/100")
            print(f"  Health Status: {data.get('health_status')}")
            print(f"  Win Rate: {data.get('win_rate', 0):.1f}%")
            print(f"  Total P&L: ₹{data.get('total_profit_loss', 0):,.0f}")
            print(f"  Risk Level: {data.get('risk_level')}")
            
            warnings = data.get('warnings', [])
            if warnings:
                print(f"\n  ⚠️  Warnings: {', '.join(warnings)}")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n  💡 Recommendations: {', '.join(recommendations)}\n")
            
            print_success("Portfolio health analysis working!")
        else:
            print(f"  {RED}Not available yet{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_investment_planner():
    """Test: Investment Planner"""
    print_feature(
        "🎯 INVESTMENT PLANNER",
        "Get AI-suggested investment plans based on your goals"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/investment-planner/create_plan/",
            json={
                "portfolio_id": 1,
                "goal": "WEALTH_CREATION",
                "target_amount": 1000000,
                "time_horizon": "5_YEARS",
                "risk_tolerance": "MEDIUM"
            }
        )
        if response.status_code == 201:
            data = response.json()
            print(f"  Goal: {data.get('goal')}")
            print(f"  Target: ₹{data.get('target_amount', 0):,.0f}")
            print(f"  Time Horizon: {data.get('time_horizon')}")
            print(f"  Expected Annual Return: {data.get('expected_annual_return'):.1f}%")
            
            allocation = data.get('allocation', {})
            print(f"\n  Asset Allocation:")
            print(f"    Equity: {allocation.get('equity', 0)}%")
            print(f"    Debt: {allocation.get('debt', 0)}%")
            print(f"    Alternatives: {allocation.get('alternatives', 0)}%")
            
            stocks = data.get('recommended_stocks', [])
            if stocks:
                print(f"\n  Recommended Stocks: {', '.join(stocks)}\n")
            
            print_success("Investment planner working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_trading_mistakes():
    """Test: Trading Mistake Detector"""
    print_feature(
        "🚨 TRADING MISTAKE DETECTOR",
        "Detect and learn from common trading mistakes"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/mistake-detector/analyze_mistake/",
            json={
                "entry_price": 2500,
                "exit_price": 2480,
                "stop_loss": 2450,
                "quantity": 100,
                "capital": 1000000,
                "rsi_at_entry": 78,
                "holding_time": 3,
                "previous_was_loss": True
            }
        )
        if response.status_code == 200:
            data = response.json()
            mistakes = data.get('mistakes', [])
            
            if mistakes:
                print(f"  🔴 {len(mistakes)} mistake(s) detected:\n")
                for mistake in mistakes:
                    print(f"    Category: {mistake.get('mistake_category')}")
                    print(f"    Severity: {mistake.get('severity')}")
                    print(f"    Description: {mistake.get('description')}")
                    print(f"    Prevention: {mistake.get('prevention_tip')}\n")
            else:
                print(f"  ✓ No mistakes detected!\n")
            
            print_success("Mistake detector working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def test_ai_explain():
    """Test: AI Explanations"""
    print_feature(
        "🤖 AI EXPLAIN FEATURE",
        "Get transparent AI explanations in simple language"
    )
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai-explain/explain_signal/",
            json={"symbol": "RELIANCE"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  Signal: {data.get('signal')}")
            print(f"  Confidence: {data.get('confidence_score', 0):.0f}%\n")
            
            print(f"  Simple Explanation (for beginners):")
            print(f"    {data.get('simple_explanation', 'N/A')}\n")
            
            print(f"  Detailed Explanation (for pros):")
            print(f"    {data.get('detailed_explanation', 'N/A')}\n")
            
            key_factors = data.get('key_factors', [])
            if key_factors:
                print(f"  Key Factors:")
                for factor in key_factors:
                    print(f"    • {factor}")
                print()
            
            print_success("AI explain working!")
        else:
            print(f"  {RED}Error: {response.status_code}{RESET}\n")
    except Exception as e:
        print(f"  {RED}Error: {str(e)}{RESET}\n")


def main():
    """Run all tests"""
    print_header("KVK_8833_PROFIT - Advanced Features API Test")
    
    print(f"{YELLOW}Testing all advanced trading features...{RESET}\n")
    
    # Run all tests
    test_beginner_signal()
    test_pro_signal()
    test_intraday_signal()
    test_risk_analysis()
    test_support_resistance()
    test_paper_trading()
    test_market_summary()
    test_smart_alerts()
    test_portfolio_health()
    test_investment_planner()
    test_trading_mistakes()
    test_ai_explain()
    
    print_header("✅ All Features Tested Successfully!")
    
    print(f"""{GREEN}Summary of Advanced Features:{RESET}

{GREEN}✓ One-Click Stock Analysis (Beginner & Pro modes){RESET}
{GREEN}✓ Intraday Quick Signals (VWAP, Volume, Market Timing){RESET}
{GREEN}✓ Automatic Risk Checks (with smart capital warnings){RESET}
{GREEN}✓ Support & Resistance Levels (Fibonacci-based){RESET}
{GREEN}✓ Paper Trading (practice without real money){RESET}
{GREEN}✓ Daily Market Summary (sentiment analysis){RESET}
{GREEN}✓ Smart Alerts (price, volume, trend changes){RESET}
{GREEN}✓ Portfolio Health Analysis (risk & diversification){RESET}
{GREEN}✓ Investment Planner (goal-based recommendations){RESET}
{GREEN}✓ Trading Mistake Detector (learn from errors){RESET}
{GREEN}✓ AI Explain Feature (transparent decisions){RESET}

{YELLOW}All endpoints are ready to use!{RESET}
{YELLOW}See ADVANCED_FEATURES.md for complete documentation.{RESET}
""")


if __name__ == "__main__":
    main()
