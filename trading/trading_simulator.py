"""
Trading Simulation Engine
Backtest strategies with real market data and calculate performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TradeSimulator:
    """Simulate trading strategies on historical data"""
    
    @staticmethod
    def backtest_strategy(
        symbol: str,
        data: pd.DataFrame,
        capital: float = 100000,
        risk_per_trade: float = 0.01,  # 1% risk
        strategy_signals: List[Dict] = None
    ) -> Dict:
        """
        Backtest a trading strategy
        
        Args:
            symbol: Stock symbol
            data: Historical OHLCV data
            capital: Initial capital
            risk_per_trade: Risk percentage per trade
            strategy_signals: Generated trading signals
        
        Returns:
            Backtest results with performance metrics
        """
        try:
            if data is None or data.empty or len(data) < 2:
                return {'error': 'Insufficient data for backtest'}
            
            # Initialize
            balance = capital
            position_size = 0
            trades = []
            equity_curve = [balance]
            entry_price = None
            
            # Simple MA crossover strategy if no signals provided
            if strategy_signals is None:
                sma_short = data['Close'].rolling(20).mean()
                sma_long = data['Close'].rolling(50).mean()
                
                for i in range(50, len(data) - 1):
                    current_price = data['Close'].iloc[i]
                    next_price = data['Close'].iloc[i + 1]
                    
                    # Generate signal
                    buy_signal = sma_short.iloc[i] > sma_long.iloc[i] and sma_short.iloc[i-1] <= sma_long.iloc[i-1]
                    sell_signal = sma_short.iloc[i] < sma_long.iloc[i] and sma_short.iloc[i-1] >= sma_long.iloc[i-1]
                    
                    # BUY
                    if buy_signal and position_size == 0 and balance > 0:
                        position_size = int(balance * 0.95 / current_price)
                        entry_price = current_price
                        balance -= position_size * current_price
                        
                        trades.append({
                            'type': 'BUY',
                            'date': data.index[i],
                            'price': current_price,
                            'quantity': position_size,
                        })
                    
                    # SELL
                    elif sell_signal and position_size > 0:
                        proceeds = position_size * next_price
                        pnl = proceeds - (position_size * entry_price)
                        pnl_percent = (pnl / (position_size * entry_price)) * 100 if entry_price > 0 else 0
                        
                        balance += proceeds
                        trades.append({
                            'type': 'SELL',
                            'date': data.index[i],
                            'price': next_price,
                            'quantity': position_size,
                            'pnl': pnl,
                            'pnl_percent': pnl_percent,
                        })
                        
                        position_size = 0
                        entry_price = None
                    
                    # Update equity curve
                    if position_size > 0:
                        position_value = position_size * current_price
                        equity_curve.append(balance + position_value)
                    else:
                        equity_curve.append(balance)
            
            # Close any open position at the end
            if position_size > 0:
                final_price = data['Close'].iloc[-1]
                proceeds = position_size * final_price
                pnl = proceeds - (position_size * entry_price)
                pnl_percent = (pnl / (position_size * entry_price)) * 100
                balance += proceeds
                position_size = 0
            
            # Calculate metrics
            equity_curve = np.array(equity_curve)
            returns = np.diff(equity_curve) / equity_curve[:-1]
            
            total_return = (equity_curve[-1] - capital) / capital * 100
            annual_return = total_return * (252 / len(data))
            volatility = np.std(returns) * np.sqrt(252) * 100
            
            # Sharpe Ratio (assuming 0% risk-free rate)
            sharpe_ratio = (annual_return / 100) / (volatility / 100) if volatility > 0 else 0
            
            # Win rate
            winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
            total_trades = len([t for t in trades if t['type'] == 'SELL'])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Max drawdown
            running_max = np.maximum.accumulate(equity_curve)
            drawdown = (equity_curve - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100
            
            return {
                'symbol': symbol,
                'initial_capital': capital,
                'final_capital': float(balance),
                'total_return': float(total_return),
                'annual_return': float(annual_return),
                'volatility': float(volatility),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(max_drawdown),
                'total_trades': len(trades),
                'winning_trades': winning_trades,
                'win_rate': float(win_rate),
                'avg_return_per_trade': float(total_return / len(trades)) if len(trades) > 0 else 0,
                'trades': trades[:10],  # Last 10 trades
                'equity_curve_start': float(equity_curve[0]),
                'equity_curve_end': float(equity_curve[-1]),
                'status': 'SUCCESS',
            }
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {'error': str(e), 'status': 'ERROR'}
    
    @staticmethod
    def calculate_position_size(
        capital: float,
        entry_price: float,
        stop_loss: float,
        risk_percent: float = 0.01
    ) -> int:
        """
        Calculate position size based on risk management
        
        Formula: Position Size = (Capital × Risk %) / (Entry - Stop Loss)
        """
        try:
            if entry_price <= 0 or stop_loss <= 0:
                return 0
            
            price_risk = abs(entry_price - stop_loss)
            if price_risk == 0:
                return 0
            
            risk_amount = capital * risk_percent
            position_size = int(risk_amount / price_risk)
            
            return position_size
        except Exception as e:
            logger.error(f"Position sizing error: {e}")
            return 0
    
    @staticmethod
    def calculate_p_and_l(
        entry_price: float,
        exit_price: float,
        quantity: int,
        commission: float = 0.001
    ) -> Dict:
        """Calculate profit and loss for a trade"""
        try:
            gross_profit = (exit_price - entry_price) * quantity
            
            # Deduct commissions (entry and exit)
            commission_cost = (entry_price + exit_price) * quantity * commission
            
            net_profit = gross_profit - commission_cost
            profit_percent = (gross_profit / (entry_price * quantity) * 100) if entry_price > 0 else 0
            
            return {
                'gross_profit': float(gross_profit),
                'commission': float(commission_cost),
                'net_profit': float(net_profit),
                'profit_percent': float(profit_percent),
                'roi': float(net_profit / (entry_price * quantity) * 100) if entry_price > 0 else 0,
            }
        except Exception as e:
            logger.error(f"P&L calculation error: {e}")
            return {}


class RiskAssessmentEngine:
    """Comprehensive risk assessment for trades"""
    
    @staticmethod
    def assess_trade_risk(
        entry_price: float,
        stop_loss: float,
        target_price: float,
        capital: float,
        portfolio_volatility: float = 0,
        market_volatility: float = 0
    ) -> Dict:
        """
        Comprehensive trade risk assessment
        """
        try:
            if entry_price <= 0:
                return {'error': 'Invalid entry price'}
            
            # Basic risk metrics
            price_risk = abs(entry_price - stop_loss)
            price_reward = abs(target_price - entry_price)
            
            risk_percent = (price_risk / entry_price) * 100
            reward_percent = (price_reward / entry_price) * 100
            risk_reward_ratio = price_reward / price_risk if price_risk > 0 else 0
            
            # Position sizing based on capital
            position_size = TradeSimulator.calculate_position_size(capital, entry_price, stop_loss)
            capital_at_risk = position_size * price_risk
            capital_risk_percent = (capital_at_risk / capital) * 100 if capital > 0 else 0
            
            # Risk levels
            if capital_risk_percent <= 0.5:
                risk_level = 'VERY_LOW'
                risk_score = 20
            elif capital_risk_percent <= 1.0:
                risk_level = 'LOW'
                risk_score = 35
            elif capital_risk_percent <= 2.0:
                risk_level = 'MODERATE'
                risk_score = 50
            elif capital_risk_percent <= 3.0:
                risk_level = 'HIGH'
                risk_score = 65
            else:
                risk_level = 'VERY_HIGH'
                risk_score = 85
            
            # Win probability based on risk/reward
            if risk_reward_ratio >= 2:
                win_probability = 80
            elif risk_reward_ratio >= 1.5:
                win_probability = 70
            elif risk_reward_ratio >= 1:
                win_probability = 60
            else:
                win_probability = 40
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'price_risk': float(price_risk),
                'price_reward': float(price_reward),
                'risk_percent': float(risk_percent),
                'reward_percent': float(reward_percent),
                'risk_reward_ratio': float(risk_reward_ratio),
                'position_size': position_size,
                'capital_at_risk': float(capital_at_risk),
                'capital_risk_percent': float(capital_risk_percent),
                'win_probability': float(win_probability),
                'expected_value': float((win_probability/100 * price_reward) - ((100-win_probability)/100 * price_risk)),
                'recommendation': 'BUY' if capital_risk_percent <= 1 else 'RECONSIDER' if capital_risk_percent <= 2 else 'AVOID',
            }
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'error': str(e)}
