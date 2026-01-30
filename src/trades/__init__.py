"""Trade recommendation module."""

from .recommend import (
    get_recommended_trades,
    TradeRecommender,
    TradeConfig,
    TradeRecommendation,
)

__all__ = [
    "get_recommended_trades",
    "TradeRecommender",
    "TradeConfig",
    "TradeRecommendation",
]
