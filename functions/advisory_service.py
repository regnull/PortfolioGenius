from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import random


@dataclass
class PortfolioPosition:
    """Represents a position in the portfolio."""
    symbol: str
    name: str
    quantity: float
    open_price: float
    current_price: float
    position_type: str  # 'stock', 'etf', 'crypto', 'bond', 'other'
    status: str  # 'open', 'closed'
    total_value: float
    gain_loss: float
    gain_loss_percent: float


@dataclass
class Trade:
    """Represents a trade transaction."""
    symbol: str
    trade_type: str  # 'buy', 'sell'
    quantity: float
    price: float
    date: datetime
    fees: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class SuggestedTrade:
    """Represents a suggested trade action."""
    symbol: str
    action: str  # 'buy', 'sell', 'hold', 'reduce'
    quantity: Optional[float]
    target_price: Optional[float]
    reasoning: str
    priority: str  # 'high', 'medium', 'low'
    risk_level: str  # 'low', 'medium', 'high'


@dataclass
class PortfolioAdvice:
    """Represents the advisory service response."""
    advice: str
    suggested_trades: List[SuggestedTrade]
    portfolio_score: float  # 0-100 rating
    risk_assessment: str
    diversification_score: float  # 0-100 rating
    timestamp: datetime


class AdvisoryService:
    """Service for analyzing portfolios and providing investment advice."""
    
    def __init__(self):
        self.hardcoded_advice_templates = [
            "Your portfolio shows a balanced approach with good diversification across sectors. Consider rebalancing to maintain optimal risk levels.",
            "The current market conditions suggest a defensive stance. Your portfolio has strong fundamentals but may benefit from some profit-taking.",
            "Your portfolio demonstrates solid growth potential with moderate risk exposure. Consider adding some value stocks for better balance.",
            "The portfolio shows good sector diversification, but concentration risk in growth stocks is notable. Consider defensive positions.",
            "Your investment strategy aligns well with your moderate risk goals. Some tactical adjustments could enhance returns.",
        ]
        
        self.hardcoded_suggestions = [
            SuggestedTrade(
                symbol="VTI",
                action="buy",
                quantity=10,
                target_price=220.0,
                reasoning="Add broad market exposure through low-cost ETF for better diversification",
                priority="medium",
                risk_level="low"
            ),
            SuggestedTrade(
                symbol="AAPL",
                action="reduce",
                quantity=5,
                target_price=175.0,
                reasoning="Take partial profits on overweight tech position to reduce concentration risk",
                priority="high",
                risk_level="medium"
            ),
            SuggestedTrade(
                symbol="JNJ",
                action="buy",
                quantity=8,
                target_price=160.0,
                reasoning="Add defensive healthcare position for portfolio stability",
                priority="medium",
                risk_level="low"
            ),
            SuggestedTrade(
                symbol="BRK.B",
                action="buy",
                quantity=15,
                target_price=420.0,
                reasoning="Add value exposure through diversified holding company",
                priority="low",
                risk_level="low"
            ),
            SuggestedTrade(
                symbol="TSLA",
                action="sell",
                quantity=None,
                target_price=200.0,
                reasoning="Reduce exposure to volatile growth stock to improve risk-adjusted returns",
                priority="high",
                risk_level="high"
            ),
        ]
    
    def analyze_portfolio(
        self,
        portfolio_goal: str,
        positions: List[PortfolioPosition],
        recent_trades: List[Trade]
    ) -> PortfolioAdvice:
        """
        Analyze portfolio and provide investment advice.
        
        Args:
            portfolio_goal: Investment goal statement
            positions: List of current portfolio positions
            recent_trades: List of recent trades
            
        Returns:
            PortfolioAdvice object with recommendations
        """
        # For now, return hardcoded advice with some randomization
        advice_text = random.choice(self.hardcoded_advice_templates)
        
        # Add goal-specific advice
        if "moderate" in portfolio_goal.lower():
            advice_text += " Your moderate risk approach is appropriate for steady long-term growth."
        elif "aggressive" in portfolio_goal.lower():
            advice_text += " Your aggressive strategy shows potential for high returns but monitor risk carefully."
        elif "conservative" in portfolio_goal.lower():
            advice_text += " Your conservative approach prioritizes capital preservation, which is prudent."
        
        # Calculate basic portfolio metrics
        portfolio_score = self._calculate_portfolio_score(positions)
        risk_assessment = self._assess_risk_level(positions)
        diversification_score = self._calculate_diversification_score(positions)
        
        # Select 2-3 random suggestions
        suggested_trades = random.sample(self.hardcoded_suggestions, k=min(3, len(self.hardcoded_suggestions)))
        
        # Customize suggestions based on existing positions
        suggested_trades = self._customize_suggestions(suggested_trades, positions)
        
        return PortfolioAdvice(
            advice=advice_text,
            suggested_trades=suggested_trades,
            portfolio_score=portfolio_score,
            risk_assessment=risk_assessment,
            diversification_score=diversification_score,
            timestamp=datetime.now()
        )
    
    def _calculate_portfolio_score(self, positions: List[PortfolioPosition]) -> float:
        """Calculate overall portfolio score (0-100)."""
        if not positions:
            return 0.0
        
        # Simple scoring based on performance
        total_gain_loss = sum(pos.gain_loss_percent for pos in positions)
        avg_performance = total_gain_loss / len(positions)
        
        # Normalize to 0-100 scale
        score = 50 + (avg_performance / 2)  # Assumes avg performance around -100% to +100%
        return max(0, min(100, score))
    
    def _assess_risk_level(self, positions: List[PortfolioPosition]) -> str:
        """Assess overall portfolio risk level."""
        if not positions:
            return "unknown"
        
        # Count high-risk positions (crypto, individual stocks with high volatility)
        high_risk_count = sum(1 for pos in positions if pos.position_type in ['crypto'])
        risk_ratio = high_risk_count / len(positions)
        
        if risk_ratio > 0.3:
            return "high"
        elif risk_ratio > 0.1:
            return "medium"
        else:
            return "low"
    
    def _calculate_diversification_score(self, positions: List[PortfolioPosition]) -> float:
        """Calculate diversification score (0-100)."""
        if not positions:
            return 0.0
        
        # Count unique position types
        position_types = set(pos.position_type for pos in positions)
        type_diversity = len(position_types) / 5  # Assuming 5 possible types
        
        # Check for concentration risk (no single position > 30% of portfolio)
        total_value = sum(pos.total_value for pos in positions)
        max_concentration = max(pos.total_value / total_value for pos in positions) if total_value > 0 else 0
        concentration_penalty = max(0, max_concentration - 0.3) * 2  # Penalty for concentration > 30%
        
        score = (type_diversity * 50) + (50 - concentration_penalty * 100)
        return max(0, min(100, score))
    
    def _customize_suggestions(
        self,
        suggestions: List[SuggestedTrade],
        positions: List[PortfolioPosition]
    ) -> List[SuggestedTrade]:
        """Customize suggestions based on existing positions."""
        existing_symbols = {pos.symbol for pos in positions}
        
        # Modify suggestions based on existing holdings
        customized = []
        for suggestion in suggestions:
            if suggestion.symbol in existing_symbols:
                # If we already hold this stock, modify the suggestion
                if suggestion.action == "buy":
                    suggestion.action = "hold"
                    suggestion.reasoning = f"You already hold {suggestion.symbol}. " + suggestion.reasoning
                elif suggestion.action == "sell":
                    suggestion.reasoning = f"Consider reducing your {suggestion.symbol} position. " + suggestion.reasoning
            
            customized.append(suggestion)
        
        return customized


# Utility functions for converting data
def dict_to_position(position_dict: Dict) -> PortfolioPosition:
    """Convert dictionary to PortfolioPosition object."""
    return PortfolioPosition(
        symbol=position_dict.get('symbol', ''),
        name=position_dict.get('name', ''),
        quantity=float(position_dict.get('quantity', 0)),
        open_price=float(position_dict.get('open_price', 0)),
        current_price=float(position_dict.get('current_price', 0)),
        position_type=position_dict.get('type', 'stock'),
        status=position_dict.get('status', 'open'),
        total_value=float(position_dict.get('total_value', 0)),
        gain_loss=float(position_dict.get('gain_loss', 0)),
        gain_loss_percent=float(position_dict.get('gain_loss_percent', 0))
    )


def dict_to_trade(trade_dict: Dict) -> Trade:
    """Convert dictionary to Trade object."""
    # Handle date conversion - could be string, datetime, or Firestore timestamp
    trade_date = trade_dict.get('date', datetime.now())
    if isinstance(trade_date, str):
        try:
            trade_date = datetime.fromisoformat(trade_date.replace('Z', '+00:00'))
        except ValueError:
            trade_date = datetime.now()
    elif hasattr(trade_date, 'to_dict'):  # Firestore timestamp
        trade_date = trade_date.to_dict()
    elif not isinstance(trade_date, datetime):
        trade_date = datetime.now()
    
    return Trade(
        symbol=trade_dict.get('symbol', ''),
        trade_type=trade_dict.get('type', 'buy'),
        quantity=float(trade_dict.get('quantity', 0)),
        price=float(trade_dict.get('price', 0)),
        date=trade_date,
        fees=float(trade_dict.get('fees', 0)) if trade_dict.get('fees') else None,
        notes=trade_dict.get('notes')
    )


def advice_to_dict(advice: PortfolioAdvice) -> Dict:
    """Convert PortfolioAdvice object to dictionary for JSON response."""
    return {
        'advice': advice.advice,
        'suggested_trades': [
            {
                'symbol': trade.symbol,
                'action': trade.action,
                'quantity': trade.quantity,
                'target_price': trade.target_price,
                'reasoning': trade.reasoning,
                'priority': trade.priority,
                'risk_level': trade.risk_level
            }
            for trade in advice.suggested_trades
        ],
        'portfolio_score': advice.portfolio_score,
        'risk_assessment': advice.risk_assessment,
        'diversification_score': advice.diversification_score,
        'timestamp': advice.timestamp.isoformat()
    }