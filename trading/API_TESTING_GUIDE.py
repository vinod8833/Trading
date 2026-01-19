import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

print(""" """)


def test_market_status():
    """Test 1: Check if market is open"""
    print("\n[TEST 1] Market Status")
    print("─" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/ai/market-status/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        data = response.json()
        if response.status_code == 200:
            print(f"✓ Market is {'OPEN' if data.get('market_open') else 'CLOSED'}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_fetch_market_data(symbol="INFY", data_type="QUOTE"):
    """Test 2: Fetch market data"""
    print(f"\n[TEST 2] Fetch Market Data - {symbol}")
    print("─" * 80)
    
    try:
        params = {
            "symbol": symbol,
            "data_type": data_type
        }
        
        response = requests.get(
            f"{BASE_URL}/api/ai/market-data/",
            params=params,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Data fetched successfully")
            print(f"  Symbol: {data.get('symbol')}")
            if data.get('quote'):
                print(f"  Price: ₹{data['quote'].get('price')}")
                print(f"  Volume: {data['quote'].get('volume'):,}")
                print(f"  Source: {data['quote'].get('source')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(json.dumps(data, indent=2))
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_data_quality(symbol="INFY"):
    """Test 3: Check data quality"""
    print(f"\n[TEST 3] Data Quality Check - {symbol}")
    print("─" * 80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/ai/data-quality/",
            params={"symbol": symbol},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Data quality checked")
            print(f"  Valid: {data.get('is_valid')}")
            print(f"  Quality: {data.get('quality')}")
            if data.get('issues'):
                print(f"  Issues: {', '.join(data['issues'])}")
            if data.get('warnings'):
                print(f"  Warnings: {', '.join(data['warnings'])}")
            print(f"  Recommendation: {data.get('recommendation')}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_generate_signal(symbol="INFY", capital=100000):
    """Test 4: Generate trading signal"""
    print(f"\n[TEST 4] Generate Trading Signal - {symbol}")
    print("─" * 80)
    
    try:
        payload = {
            "symbol": symbol,
            "capital": capital,
            "trader_type": "SWING"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-signal/",
            json=payload,
            timeout=15  
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Signal generated successfully")
            print(f"  Signal Type: {data.get('signal', {}).get('type')}")
            print(f"  Confidence: {data.get('signal', {}).get('confidence'):.1f}%")
            print(f"  Entry: ₹{data.get('execution', {}).get('entry', 0):.2f}")
            print(f"  Stop Loss: ₹{data.get('execution', {}).get('stop_loss', 0):.2f}")
            print(f"  Target 1: ₹{data.get('execution', {}).get('target_1', 0):.2f}")
            print(f"  Target 2: ₹{data.get('execution', {}).get('target_2', 0):.2f}")
            print(f"  Risk/Reward: 1:{data.get('risk', {}).get('risk_reward_ratio', 0):.1f}")
            print(f"  Market Status: {data.get('market', {}).get('status')}")
            print(f"  Executable: {data.get('signal', {}).get('is_executable')}")
            
            if data.get('metadata', {}).get('warnings'):
                print(f"  Warnings: {', '.join(data['metadata']['warnings'])}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            if 'error' in data:
                print(f"  {data['error']}")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_calculate_indicators(symbol="INFY"):
    """Test 5: Calculate technical indicators"""
    print(f"\n[TEST 5] Calculate Technical Indicators - {symbol}")
    print("─" * 80)
    
    try:
        # First fetch historical data
        print("  Fetching historical data for indicators...")
        market_data = requests.get(
            f"{BASE_URL}/api/ai/market-data/",
            params={"symbol": symbol, "data_type": "HISTORICAL"},
            timeout=10
        ).json()
        
        candles = market_data.get('historical', {}).get('candles', [])
        
        if not candles:
            print(f"✗ No candles available")
            return False
        
        # Convert candles format
        formatted_candles = [
            {
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"]
            }
            for c in candles[-100:]  # Use last 100
        ]
        
        payload = {
            "symbol": symbol,
            "candles": formatted_candles
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/calculate-indicators/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Indicators calculated successfully")
            
            trend = data.get('trend', {})
            print(f"  Trend Indicators:")
            print(f"    EMA 20: {trend.get('ema_20', 0):.2f}")
            print(f"    EMA 50: {trend.get('ema_50', 0):.2f}")
            print(f"    EMA 100: {trend.get('ema_100', 0):.2f}")
            print(f"    EMA 200: {trend.get('ema_200', 0):.2f}")
            
            momentum = data.get('momentum', {})
            print(f"  Momentum Indicators:")
            print(f"    RSI: {momentum.get('rsi', 0):.2f} ({momentum.get('rsi_signal', 'N/A')})")
            print(f"    MACD: {momentum.get('macd_line', 0):.4f}")
            print(f"    MACD Signal: {momentum.get('macd_signal', 'N/A')}")
            
            volatility = data.get('volatility', {})
            print(f"  Volatility Indicators:")
            print(f"    ATR: {volatility.get('atr', 0):.2f}")
            print(f"    ATR%: {volatility.get('atr_percent', 0):.2f}%")
            
            levels = data.get('levels', {})
            print(f"  Support/Resistance:")
            print(f"    Support 1: {levels.get('support_1', 0):.2f}")
            print(f"    Resistance 1: {levels.get('resistance_1', 0):.2f}")
            print(f"    Pivot: {levels.get('pivot', 0):.2f}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_predict_movement(symbol="INFY"):
    """Test 6: Predict 5-minute price movement"""
    print(f"\n[TEST 6] Predict 5-Minute Movement - {symbol}")
    print("─" * 80)
    
    try:
        print("  Fetching intraday data...")
        market_data = requests.get(
            f"{BASE_URL}/api/ai/market-data/",
            params={"symbol": symbol, "data_type": "ALL"},
            timeout=10
        ).json()
        
        quote = market_data.get('quote', {})
        intraday_candles = market_data.get('intraday', {}).get('candles', [])
        
        if not intraday_candles:
            print(f"✗ No intraday data available")
            return False
        
        print("  Getting indicators...")
        # Get indicators first
        historical = market_data.get('historical', {}).get('candles', [])
        formatted_candles = [
            {
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"]
            }
            for c in historical[-100:]
        ]
        
        ind_response = requests.post(
            f"{BASE_URL}/api/ai/calculate-indicators/",
            json={"symbol": symbol, "candles": formatted_candles},
            timeout=10
        ).json()
        
        # Format intraday candles
        formatted_intraday = [
            {
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"]
            }
            for c in intraday_candles[-50:]
        ]
        
        payload = {
            "symbol": symbol,
            "candles": formatted_intraday,
            "indicators": ind_response,
            "current_price": quote.get("price", 0)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/predict-movement/",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✓ Prediction generated successfully")
            print(f"  Direction: {data.get('direction')}")
            print(f"  Confidence: {data.get('confidence', 0):.1f}%")
            print(f"  Predicted Price: ₹{data.get('predicted_price', 0):.2f}")
            print(f"  Change: {data.get('predicted_change_percent', 0):.2f}%")
            
            rr = data.get('risk_reward', {})
            print(f"  Stop Loss: ₹{rr.get('stop_loss', 0):.2f}")
            print(f"  Target: ₹{rr.get('target', 0):.2f}")
            
            factors = data.get('factors', [])
            print(f"  Factors: {', '.join(factors[:3])}")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "=" * 80)
    print("RUNNING ALL TESTS")
    print("=" * 80)
    
    tests = [
        ("Market Status", test_market_status),
        ("Fetch Market Data", lambda: test_fetch_market_data("INFY", "QUOTE")),
        ("Data Quality", lambda: test_data_quality("INFY")),
        ("Generate Signal", lambda: test_generate_signal("INFY", 100000)),
        ("Calculate Indicators", lambda: test_calculate_indicators("INFY")),
        ("Predict Movement", lambda: test_predict_movement("INFY")),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = "✓ PASS" if result else "✗ FAIL"
        except Exception as e:
            results[name] = f"✗ ERROR: {str(e)[:30]}"
        
        time.sleep(0.5)  # Rate limit
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, result in results.items():
        print(f"{name:.<40} {result}")


# ═══════════════════════════════════════════════════════════════════════════
# QUICK EXAMPLES FOR COPY-PASTE
# ═══════════════════════════════════════════════════════════════════════════

EXAMPLES = """

EXAMPLE 1: Check if market is open
──────────────────────────────────
import requests

response = requests.get("http://localhost:8001/api/ai/market-status/")
print(response.json())


EXAMPLE 2: Generate a trading signal
──────────────────────────────────
import requests

response = requests.post(
    "http://localhost:8001/api/ai/generate-signal/",
    json={
        "symbol": "INFY",
        "capital": 100000,
        "trader_type": "SWING"
    }
)

signal = response.json()
print(f"Signal: {signal['signal']['type']}")
print(f"Entry: ₹{signal['execution']['entry']}")
print(f"Stop Loss: ₹{signal['execution']['stop_loss']}")
print(f"Target: ₹{signal['execution']['target_1']}")


EXAMPLE 3: Get market data
──────────────────────────────────
import requests

response = requests.get(
    "http://localhost:8001/api/ai/market-data/",
    params={
        "symbol": "INFY",
        "data_type": "QUOTE"  # or HISTORICAL, INTRADAY, ALL
    }
)

print(response.json())


EXAMPLE 4: Check data quality
──────────────────────────────────
import requests

response = requests.get(
    "http://localhost:8001/api/ai/data-quality/",
    params={"symbol": "INFY"}
)

data = response.json()
print(f"Valid: {data['is_valid']}")
print(f"Issues: {data.get('issues', [])}")


EXAMPLE 5: Loop to refresh signals every 5 minutes
──────────────────────────────────
import requests
import time

symbols = ["INFY", "TCS", "HDFC"]

while True:
    for symbol in symbols:
        response = requests.post(
            "http://localhost:8001/api/ai/generate-signal/",
            json={
                "symbol": symbol,
                "capital": 100000,
                "trader_type": "SWING"
            }
        )
        
        signal = response.json()
        if signal.get('signal', {}).get('type') != 'HOLD':
            print(f"{symbol}: {signal['signal']['type']} " +
                  f"@ {signal['execution']['entry']:.2f}")
    
    # Wait 5 minutes
    time.sleep(5 * 60)
"""

if __name__ == "__main__":
    # Show examples
    print(EXAMPLES)
    
    # Run tests
    print("\n\nTo run tests, uncomment the line below:")
    print("# run_all_tests()")
    
    print("\n\nOr run individual tests:")
    print("# test_market_status()")
    print("# test_generate_signal('INFY', 100000)")
    print("\n")
