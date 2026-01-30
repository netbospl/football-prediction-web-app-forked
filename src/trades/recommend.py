"""Trade recommendation engine with explainability.

Scoring methodology:
- Only considers matches with unknown F_RESULT (upcoming fixtures)
- Model confidence proxy: derived from abs(PRED_DIFF) using sigmoid normalization
- Market implied probability: 1 / odds
- Edge: model_confidence - market_implied_prob
- EV (Expected Value): edge * (odds - 1)
- Stake sizing: Kelly-lite formula clamped to max % of bankroll

Explainability:
- Uses SHAP data to extract top contributing features
- Presents 2-4 bullet reasons per match explaining the recommendation
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from ..utils.config import Config as cfg


@dataclass
class TradeConfig:
    """Configuration for trade recommendation."""
    # Minimum edge (model_conf - implied_prob) to consider a trade
    min_edge: float = 0.05
    # Minimum score to recommend
    min_score: float = 0.1
    # Maximum stake as fraction of bankroll (Kelly clamp)
    max_stake_pct: float = 0.05
    # Bankroll for stake calculation
    bankroll: float = 100.0
    # Minimum odds to consider
    min_odds: float = 1.2
    # Maximum odds to consider
    max_odds: float = 10.0
    # Number of top trades to return
    top_n: int = 10
    # SHAP features to show in explanation
    top_shap_features: int = 4


@dataclass
class TradeRecommendation:
    """A single trade recommendation with rationale."""
    match_key: str
    date: str
    time: str
    division: str
    home_team: str
    away_team: str
    side: str  # "H", "D", or "A"
    odds: float
    model_confidence: float
    implied_prob: float
    edge: float
    ev: float
    score: float
    stake: float
    stake_pct: float
    rationale: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DB storage."""
        return {
            "match_key": self.match_key,
            "side": self.side,
            "odds": self.odds,
            "score": self.score,
            "edge": self.edge,
            "ev": self.ev,
            "stake": self.stake,
            "rationale": self.rationale
        }


class TradeRecommender:
    """Generates trade recommendations from prediction data."""

    def __init__(self, config: Optional[TradeConfig] = None):
        self.config = config or TradeConfig()

    def recommend(self, df: pd.DataFrame) -> List[TradeRecommendation]:
        """Generate trade recommendations from predictions DataFrame.

        Args:
            df: DataFrame with predictions, odds, and optionally SHAP columns

        Returns:
            List of TradeRecommendation objects sorted by score (descending)
        """
        # Filter to upcoming fixtures only (no result yet)
        upcoming = self._filter_upcoming(df)
        if upcoming.empty:
            return []

        recommendations = []
        for idx, row in upcoming.iterrows():
            rec = self._evaluate_match(row)
            if rec is not None:
                recommendations.append(rec)

        # Sort by score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)

        # Return top N
        return recommendations[:self.config.top_n]

    def _filter_upcoming(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter to upcoming fixtures (F_RESULT is NaN or empty)."""
        if "F_RESULT" not in df.columns:
            return df

        # F_RESULT is NaN for upcoming matches
        mask = df["F_RESULT"].isna() | (df["F_RESULT"] == "")
        return df[mask].copy()

    def _evaluate_match(self, row: pd.Series) -> Optional[TradeRecommendation]:
        """Evaluate a single match for trade potential.

        Args:
            row: DataFrame row with prediction data

        Returns:
            TradeRecommendation if trade is recommended, None otherwise
        """
        # Get predicted result and odds
        pred_result_num = row.get("PRED_RESULT_NUM")
        if pd.isna(pred_result_num):
            return None

        side = cfg.PRED_MAPPING.get(pred_result_num)
        if side is None:
            return None

        # Get odds for predicted side
        odds_col = f"ODDS_{side}_MAX"
        odds = row.get(odds_col)
        if pd.isna(odds) or odds < self.config.min_odds or odds > self.config.max_odds:
            return None

        # Calculate model confidence from PRED_DIFF
        pred_diff = row.get("PRED_DIFF", 0)
        model_conf = self._calc_model_confidence(pred_diff)

        # Calculate implied probability from odds
        implied_prob = 1.0 / odds

        # Calculate edge
        edge = model_conf - implied_prob
        if edge < self.config.min_edge:
            return None

        # Calculate EV
        ev = edge * (odds - 1)

        # Calculate score (composite metric)
        score = self._calc_score(edge, ev, odds)
        if score < self.config.min_score:
            return None

        # Calculate stake using Kelly-lite
        stake_pct = self._calc_kelly_stake(edge, odds)
        stake = stake_pct * self.config.bankroll

        # Generate rationale with SHAP explanation
        rationale = self._generate_rationale(row, side, model_conf, implied_prob, edge)

        # Create match key
        date_str = str(row.get("F_DATE", ""))[:10]
        match_key = f"{date_str}_{row.get('F_DIV')}_{row.get('F_H_TEAM')}_{row.get('F_A_TEAM')}"

        return TradeRecommendation(
            match_key=match_key,
            date=str(row.get("F_DATE", ""))[:10],
            time=str(row.get("F_TIME", "")),
            division=row.get("F_DIV", ""),
            home_team=row.get("F_H_TEAM", ""),
            away_team=row.get("F_A_TEAM", ""),
            side=side,
            odds=round(odds, 2),
            model_confidence=round(model_conf, 4),
            implied_prob=round(implied_prob, 4),
            edge=round(edge, 4),
            ev=round(ev, 4),
            score=round(score, 4),
            stake=round(stake, 2),
            stake_pct=round(stake_pct, 4),
            rationale=rationale
        )

    def _calc_model_confidence(self, pred_diff: float) -> float:
        """Calculate model confidence from predicted goal difference.

        Uses a scaled sigmoid function to map abs(PRED_DIFF) to probability.
        The sigmoid 1/(1+exp(-kx)) naturally maps:
        - x = 0 → 0.5 (uncertain)
        - x = 1 → ~0.73 (k=1)
        - x = 2 → ~0.88 (k=1)
        - x = 3 → ~0.95 (k=1)

        Args:
            pred_diff: Predicted goal difference

        Returns:
            Confidence value between 0.5 and 1.0
        """
        # Use standard sigmoid: 1 / (1 + exp(-kx))
        # k controls steepness (higher = steeper transition)
        k = 1.0
        x = abs(pred_diff) if pd.notna(pred_diff) else 0
        # Sigmoid naturally gives 0.5 at x=0, approaches 1 as x increases
        return 1.0 / (1.0 + math.exp(-k * x))

    def _calc_score(self, edge: float, ev: float, odds: float) -> float:
        """Calculate composite trade score.

        Score combines:
        - Edge (model advantage over market)
        - EV (expected value)
        - Odds sweetspot bonus (prefer moderate odds)

        Args:
            edge: Model edge over implied probability
            ev: Expected value
            odds: Betting odds

        Returns:
            Composite score
        """
        # Odds sweetspot: prefer 1.8-4.0 range
        odds_bonus = 1.0
        if 1.8 <= odds <= 4.0:
            odds_bonus = 1.2
        elif odds > 6.0:
            odds_bonus = 0.8

        # Combine factors
        return (edge * 0.4 + ev * 0.4 + min(edge, 0.2) * 0.2) * odds_bonus

    def _calc_kelly_stake(self, edge: float, odds: float) -> float:
        """Calculate Kelly-lite stake percentage.

        Kelly criterion: stake = edge / (odds - 1)
        We use fractional Kelly (typically 1/4 to 1/2) and clamp.

        Args:
            edge: Model edge
            odds: Betting odds

        Returns:
            Stake as fraction of bankroll
        """
        if odds <= 1:
            return 0

        # Full Kelly
        kelly = edge / (odds - 1)

        # Use quarter Kelly for safety
        quarter_kelly = kelly / 4

        # Clamp to max stake
        return min(max(quarter_kelly, 0), self.config.max_stake_pct)

    def _generate_rationale(self, row: pd.Series, side: str,
                           model_conf: float, implied_prob: float,
                           edge: float) -> Dict[str, Any]:
        """Generate human-readable rationale for the trade.

        Args:
            row: DataFrame row with prediction and SHAP data
            side: Predicted outcome ("H", "D", "A")
            model_conf: Model confidence
            implied_prob: Market implied probability
            edge: Calculated edge

        Returns:
            Dictionary with rationale components
        """
        rationale = {
            "summary": self._create_summary(side, model_conf, implied_prob, edge),
            "bullets": [],
            "shap_drivers": {}
        }

        # Add probability comparison
        side_name = {"H": "Home win", "D": "Draw", "A": "Away win"}.get(side, side)
        rationale["bullets"].append(
            f"Model predicts {side_name} with {model_conf*100:.1f}% confidence"
        )
        rationale["bullets"].append(
            f"Market implies {implied_prob*100:.1f}% probability (edge: {edge*100:.1f}%)"
        )

        # Extract SHAP drivers
        shap_drivers = self._extract_shap_drivers(row)
        if shap_drivers:
            rationale["shap_drivers"] = shap_drivers

            # Add SHAP-based bullets
            positive_features = [f for f, v in shap_drivers.items() if v > 0]
            negative_features = [f for f, v in shap_drivers.items() if v < 0]

            if positive_features:
                pos_str = ", ".join(positive_features[:2])
                rationale["bullets"].append(f"Model favors {side_name} due to: {pos_str}")

            if negative_features:
                neg_str = ", ".join(negative_features[:2])
                rationale["bullets"].append(f"Risk factors: {neg_str}")

        return rationale

    def _create_summary(self, side: str, model_conf: float,
                       implied_prob: float, edge: float) -> str:
        """Create one-line summary of the trade rationale."""
        side_name = {"H": "Home", "D": "Draw", "A": "Away"}.get(side, side)
        return (f"{side_name}: model {model_conf*100:.0f}% vs market "
                f"{implied_prob*100:.0f}% = {edge*100:.1f}% edge")

    def _extract_shap_drivers(self, row: pd.Series) -> Dict[str, float]:
        """Extract top SHAP features driving the prediction.

        Args:
            row: DataFrame row with SHAP columns

        Returns:
            Dictionary of feature name → SHAP value (sorted by abs value)
        """
        shap_cols = [c for c in row.index if c.startswith("SHAP_") and c != "SHAP_INTERCEPT"]

        if not shap_cols:
            return {}

        # Get non-zero SHAP values
        shap_values = []
        for col in shap_cols:
            val = row[col]
            if pd.notna(val) and val != 0:
                feature_name = col.replace("SHAP_", "")
                shap_values.append((feature_name, val))

        # Sort by absolute value
        shap_values.sort(key=lambda x: abs(x[1]), reverse=True)

        # Return top N
        return {f: round(v, 4) for f, v in shap_values[:self.config.top_shap_features]}


def get_recommended_trades(df: pd.DataFrame,
                          config: Optional[TradeConfig] = None) -> List[TradeRecommendation]:
    """Convenience function to get trade recommendations.

    Args:
        df: DataFrame with predictions
        config: Optional TradeConfig

    Returns:
        List of TradeRecommendation objects
    """
    recommender = TradeRecommender(config)
    return recommender.recommend(df)
