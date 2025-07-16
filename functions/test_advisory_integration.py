#!/usr/bin/env python3
"""
Test script for the portfolio advisory integration.
This tests the core logic without requiring Firebase authentication.
"""

import json
from unittest.mock import Mock, patch
from advisory_service import AdvisoryService, dict_to_position, dict_to_trade
from datetime import datetime


def test_portfolio_advisory_logic():
    """Test the core portfolio advisory logic."""
    print("Testing Portfolio Advisory Integration Logic...")
    
    # Mock portfolio data
    portfolio_data = {
        'userId': 'test-user-123',
        'goal': 'Design a moderate-risk investment portfolio aimed at achieving steady long-term growth',
        'name': 'Test Portfolio'
    }
    
    # Mock positions data (simulating Firestore format)
    positions_data = [
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'quantity': 10,
            'openPrice': 150.0,
            'currentPrice': 175.0,
            'type': 'stock',
            'status': 'open',
            'totalValue': 1750.0,
            'gainLoss': 250.0,
            'gainLossPercent': 16.67
        },
        {
            'symbol': 'VTI',
            'name': 'Vanguard Total Stock Market ETF',
            'quantity': 50,
            'openPrice': 200.0,
            'currentPrice': 220.0,
            'type': 'etf',
            'status': 'open',
            'totalValue': 11000.0,
            'gainLoss': 1000.0,
            'gainLossPercent': 10.0
        }
    ]
    
    # Mock trades data (simulating Firestore format)
    trades_data = [
        {
            'symbol': 'AAPL',
            'type': 'buy',
            'quantity': 5,
            'price': 160.0,
            'date': datetime.now(),
            'fees': 1.0,
            'notes': 'Adding to position'
        }
    ]
    
    # Convert to advisory service format
    positions = []
    for pos_data in positions_data:
        positions.append(dict_to_position({
            'symbol': pos_data['symbol'],
            'name': pos_data['name'],
            'quantity': pos_data['quantity'],
            'open_price': pos_data['openPrice'],
            'current_price': pos_data['currentPrice'],
            'type': pos_data['type'],
            'status': pos_data['status'],
            'total_value': pos_data['totalValue'],
            'gain_loss': pos_data['gainLoss'],
            'gain_loss_percent': pos_data['gainLossPercent']
        }))
    
    trades = []
    for trade_data in trades_data:
        trades.append(dict_to_trade({
            'symbol': trade_data['symbol'],
            'type': trade_data['type'],
            'quantity': trade_data['quantity'],
            'price': trade_data['price'],
            'date': trade_data['date'],
            'fees': trade_data.get('fees'),
            'notes': trade_data.get('notes')
        }))
    
    # Generate advisory
    advisory_service = AdvisoryService()
    advice = advisory_service.analyze_portfolio(
        portfolio_goal=portfolio_data['goal'],
        positions=positions,
        recent_trades=trades
    )
    
    print("\n" + "="*60)
    print("PORTFOLIO ADVISORY INTEGRATION TEST")
    print("="*60)
    
    print(f"\nPortfolio: {portfolio_data['name']}")
    print(f"Goal: {portfolio_data['goal']}")
    print(f"Positions: {len(positions)}")
    print(f"Recent Trades: {len(trades)}")
    
    print(f"\nGenerated Advice:")
    print(f"  {advice.advice}")
    
    print(f"\nPortfolio Metrics:")
    print(f"  Score: {advice.portfolio_score:.1f}/100")
    print(f"  Risk Assessment: {advice.risk_assessment}")
    print(f"  Diversification Score: {advice.diversification_score:.1f}/100")
    
    print(f"\nSuggested Trades ({len(advice.suggested_trades)}):")
    for i, trade in enumerate(advice.suggested_trades, 1):
        print(f"  {i}. {trade.action.upper()} {trade.symbol}")
        print(f"     Priority: {trade.priority}")
        print(f"     Risk Level: {trade.risk_level}")
        if trade.quantity:
            print(f"     Quantity: {trade.quantity}")
        if trade.target_price:
            print(f"     Target Price: ${trade.target_price:.2f}")
        print(f"     Reasoning: {trade.reasoning}")
        print()
    
    # Test Firestore data structure
    print("Testing Firestore Data Structures:")
    
    # Simulate suggested trades collection structure
    suggested_trades_firestore = []
    for trade in advice.suggested_trades:
        suggested_trades_firestore.append({
            'symbol': trade.symbol,
            'action': trade.action,
            'quantity': trade.quantity,
            'targetPrice': trade.target_price,
            'reasoning': trade.reasoning,
            'priority': trade.priority,
            'riskLevel': trade.risk_level,
            'createdAt': 'SERVER_TIMESTAMP',
            'status': 'pending'
        })
    
    print(f"  Suggested Trades Collection: {len(suggested_trades_firestore)} documents")
    
    # Simulate portfolio document update
    portfolio_update = {
        'advice': advice.advice,
        'portfolioScore': advice.portfolio_score,
        'riskAssessment': advice.risk_assessment,
        'diversificationScore': advice.diversification_score,
        'lastAdvisoryDate': 'SERVER_TIMESTAMP',
        'updatedAt': 'SERVER_TIMESTAMP'
    }
    
    print(f"  Portfolio Document Fields: {len(portfolio_update)} fields updated")
    
    # Test JSON serialization
    response_data = {
        "success": True,
        "message": "Portfolio advisory generated successfully",
        "data": {
            "portfolio_id": "test-portfolio-123",
            "advice": advice.advice,
            "portfolio_score": advice.portfolio_score,
            "risk_assessment": advice.risk_assessment,
            "diversification_score": advice.diversification_score,
            "suggested_trades_count": len(advice.suggested_trades)
        },
        "user_id": "test-user-123",
        "timestamp": advice.timestamp.isoformat()
    }
    
    json_response = json.dumps(response_data, indent=2)
    print(f"  JSON Response: {len(json_response)} characters")
    
    print("\n" + "="*60)
    print("✅ Integration test completed successfully!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        test_portfolio_advisory_logic()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()