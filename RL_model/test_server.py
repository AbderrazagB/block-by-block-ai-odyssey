"""
Test script for the Trading Model Server
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"


def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")


def test_model_info():
    """Test model info endpoint"""
    print("\n2. Testing Model Info...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Tickers: {len(data['tickers'])} stocks")
    print(f"   Indicators: {data['indicators']}")
    print(f"   Initial Amount: ${data['initial_amount']:,}")


def test_backtest_summary():
    """Test backtest summary endpoint"""
    print("\n3. Testing Backtest Summary...")
    response = requests.get(f"{BASE_URL}/backtest/summary")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   Summary:")
            for item in data['summary']:
                print(f"      {item['Metric']}: {item['Value']}")


def test_prediction():
    """Test prediction endpoint"""
    print("\n4. Testing Predictions...")
    # Use a date 2 days ago
    test_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"date": test_date}
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"   Prediction Date: {data['date']}")
            print(f"   Top 5 Recommendations:")
            
            # Sort by absolute action value
            predictions = data['predictions']
            sorted_stocks = sorted(
                predictions.items(),
                key=lambda x: abs(x[1]['action']),
                reverse=True
            )[:5]
            
            for ticker, info in sorted_stocks:
                print(f"      {ticker}: {info['recommendation']} "
                      f"(action: {info['action']:.4f}, price: ${info['current_price']:.2f})")


def test_model_testing():
    """Test the model testing endpoint"""
    print("\n5. Testing Model on Recent Data...")
    
    # Test from training end to 2 days ago
    end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = "2024-01-01"  # Test on 2024 data
    
    print(f"   Testing period: {start_date} to {end_date}")
    print("   This may take a minute...")
    
    response = requests.post(
        f"{BASE_URL}/test",
        json={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            results = data['results']
            print(f"   Trading Days: {len(results['dates'])}")
            print(f"   Initial Value: ${results['initial_value']:,.2f}")
            print(f"   Final Value: ${results['final_value']:,.2f}")
            print(f"   Total Return: {results['total_return']:.2f}%")
            print(f"   Number of stocks tracked: {len(results['tickers'])}")


if __name__ == "__main__":
    print("="*60)
    print("Trading Model Server - Test Suite")
    print("="*60)
    print("\nMake sure the server is running on http://localhost:5000")
    
    try:
        test_health()
        test_model_info()
        test_backtest_summary()
        test_prediction()
        test_model_testing()
        
        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running: python trading_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
