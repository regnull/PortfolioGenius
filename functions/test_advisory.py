#!/usr/bin/env python3
"""
Test script for the advisory service.
"""

from advisory_service import AdvisoryService, PortfolioPosition, Trade, dict_to_position, dict_to_trade, advice_to_dict
from datetime import datetime
import json


def test_advisory_service():
    """Test the advisory service with sample data."""
    print("Testing Advisory Service...")
    
    # Sample portfolio goal
    portfolio_goal = "Design a moderate-risk investment portfolio aimed at achieving steady long-term growth"
    
    # Sample positions
    sample_positions = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 10,
            "open_price": 150.0,
            "current_price": 175.0,
            "type": "stock",
            "status": "open",
            "total_value": 1750.0,
            "gain_loss": 250.0,
            "gain_loss_percent": 16.67
        },
        {
            "symbol": "VTI",
            "name": "Vanguard Total Stock Market ETF",
            "quantity": 50,
            "open_price": 200.0,
            "current_price": 220.0,
            "type": "etf",
            "status": "open",
            "total_value": 11000.0,
            "gain_loss": 1000.0,
            "gain_loss_percent": 10.0
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "quantity": 15,
            "open_price": 300.0,
            "current_price": 350.0,
            "type": "stock",
            "status": "open",
            "total_value": 5250.0,
            "gain_loss": 750.0,
            "gain_loss_percent": 16.67
        }
    ]
    
    # Sample recent trades
    sample_trades = [
        {
            "symbol": "AAPL",
            "type": "buy",
            "quantity": 5,
            "price": 160.0,
            "date": "2024-01-15T10:30:00",
            "fees": 1.0,
            "notes": "Adding to position"
        },
        {
            "symbol": "VTI",
            "type": "buy",
            "quantity": 25,
            "price": 210.0,
            "date": "2024-01-10T14:15:00",
            "fees": 0.0,
            "notes": "Monthly investment"
        }
    ]
    
    # Convert to objects
    positions = [dict_to_position(pos) for pos in sample_positions]
    trades = [dict_to_trade(trade) for trade in sample_trades]
    
    # Test the advisory service
    advisory_service = AdvisoryService()
    advice = advisory_service.analyze_portfolio(
        portfolio_goal=portfolio_goal,
        positions=positions,
        recent_trades=trades
    )
    
    # Convert to dictionary for display
    advice_dict = advice_to_dict(advice)
    
    print("\n" + "="*50)
    print("PORTFOLIO ADVISORY REPORT")
    print("="*50)
    
    print(f"\nPortfolio Goal: {portfolio_goal}")
    print(f"\nPortfolio Score: {advice_dict['portfolio_score']:.1f}/100")
    print(f"Risk Assessment: {advice_dict['risk_assessment']}")
    print(f"Diversification Score: {advice_dict['diversification_score']:.1f}/100")
    
    print(f"\nAdvice:")
    print(f"  {advice_dict['advice']}")
    
    print(f"\nSuggested Trades:")
    for i, trade in enumerate(advice_dict['suggested_trades'], 1):
        print(f"  {i}. {trade['action'].upper()} {trade['symbol']}")
        print(f"     Priority: {trade['priority']}")
        print(f"     Risk Level: {trade['risk_level']}")
        if trade['quantity']:
            print(f"     Quantity: {trade['quantity']}")
        if trade['target_price']:
            print(f"     Target Price: ${trade['target_price']:.2f}")
        print(f"     Reasoning: {trade['reasoning']}")
        print()
    
    print(f"Report Generated: {advice_dict['timestamp']}")
    print("="*50)
    
    # Test JSON serialization
    json_response = json.dumps(advice_dict, indent=2)
    print(f"\nJSON Response Length: {len(json_response)} characters")
    print("JSON serialization: SUCCESS")
    
    return True


if __name__ == "__main__":
    try:
        test_advisory_service()
        print("\n✅ Advisory service test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()