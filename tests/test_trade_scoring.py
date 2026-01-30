"""Test trade scoring and recommendation logic."""

import pytest
import pandas as pd
import numpy as np

from src.trades.recommend import (
    TradeRecommender,
    TradeConfig,
    TradeRecommendation,
    get_recommended_trades
)


@pytest.fixture
def sample_upcoming_df():
    """Create a sample DataFrame with upcoming fixtures."""
    return pd.DataFrame({
        'F_DATE': pd.to_datetime(['2024-12-15', '2024-12-15', '2024-12-16']),
        'F_TIME': ['15:00', '17:30', '14:00'],
        'F_DIV': ['E0', 'E0', 'D1'],
        'F_H_TEAM': ['Arsenal', 'Liverpool', 'Bayern'],
        'F_A_TEAM': ['Chelsea', 'Man City', 'Dortmund'],
        'F_RESULT': [np.nan, np.nan, np.nan],  # Upcoming = no result
        'PRED_RESULT_NUM': [1.0, -1.0, 0.0],  # H, A, D
        'PRED_DIFF': [1.5, -0.8, 0.1],
        'ODDS_H_MAX': [2.5, 3.2, 2.8],
        'ODDS_D_MAX': [3.4, 3.5, 3.2],
        'ODDS_A_MAX': [2.8, 2.1, 2.6],
        'SHAP_FEATURE_A': [0.15, -0.10, 0.05],
        'SHAP_FEATURE_B': [-0.08, 0.12, -0.03],
        'SHAP_INTERCEPT': [0.0, 0.0, 0.0],
    })


@pytest.fixture
def sample_completed_df():
    """Create a sample DataFrame with completed matches (should be filtered out)."""
    return pd.DataFrame({
        'F_DATE': pd.to_datetime(['2024-12-10', '2024-12-11']),
        'F_TIME': ['15:00', '17:30'],
        'F_DIV': ['E0', 'E0'],
        'F_H_TEAM': ['Arsenal', 'Liverpool'],
        'F_A_TEAM': ['Chelsea', 'Man City'],
        'F_RESULT': ['H', 'D'],  # Has result = completed
        'PRED_RESULT_NUM': [1.0, 0.0],
        'PRED_DIFF': [1.5, 0.1],
        'ODDS_H_MAX': [2.5, 3.2],
        'ODDS_D_MAX': [3.4, 3.5],
        'ODDS_A_MAX': [2.8, 2.1],
    })


class TestTradeConfig:
    """Test TradeConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TradeConfig()
        assert config.min_edge == 0.05
        assert config.min_score == 0.1
        assert config.max_stake_pct == 0.05
        assert config.bankroll == 100.0
        assert config.min_odds == 1.2
        assert config.max_odds == 10.0
        assert config.top_n == 10

    def test_custom_values(self):
        """Test custom configuration."""
        config = TradeConfig(
            min_edge=0.10,
            bankroll=500.0,
            top_n=5
        )
        assert config.min_edge == 0.10
        assert config.bankroll == 500.0
        assert config.top_n == 5


class TestTradeRecommender:
    """Test TradeRecommender class."""

    def test_filter_upcoming(self, sample_upcoming_df):
        """Test that only upcoming fixtures are considered."""
        recommender = TradeRecommender()
        filtered = recommender._filter_upcoming(sample_upcoming_df)
        assert len(filtered) == 3
        assert filtered['F_RESULT'].isna().all()

    def test_filter_completed(self, sample_completed_df):
        """Test that completed matches are filtered out."""
        recommender = TradeRecommender()
        filtered = recommender._filter_upcoming(sample_completed_df)
        assert len(filtered) == 0

    def test_model_confidence_calculation(self):
        """Test model confidence is calculated correctly."""
        recommender = TradeRecommender()

        # Zero diff should give 0.5 confidence
        conf_zero = recommender._calc_model_confidence(0)
        assert abs(conf_zero - 0.5) < 0.01

        # Higher diff should give higher confidence
        conf_1 = recommender._calc_model_confidence(1.0)
        conf_2 = recommender._calc_model_confidence(2.0)
        assert conf_1 > conf_zero
        assert conf_2 > conf_1

        # Negative diff should work the same (absolute value)
        conf_neg = recommender._calc_model_confidence(-1.0)
        assert abs(conf_neg - conf_1) < 0.01

        # Confidence should be bounded
        conf_extreme = recommender._calc_model_confidence(10.0)
        assert 0.5 <= conf_extreme <= 1.0

    def test_kelly_stake_calculation(self):
        """Test Kelly stake is calculated and clamped correctly."""
        recommender = TradeRecommender(TradeConfig(max_stake_pct=0.05))

        # Positive edge should give positive stake
        stake = recommender._calc_kelly_stake(0.10, 2.0)
        assert stake > 0

        # Stake should be clamped
        assert stake <= 0.05

        # Zero edge should give zero stake
        stake_zero = recommender._calc_kelly_stake(0, 2.0)
        assert stake_zero == 0

        # Negative edge should give zero stake
        stake_neg = recommender._calc_kelly_stake(-0.1, 2.0)
        assert stake_neg == 0

    def test_score_calculation(self):
        """Test score is deterministic and reasonable."""
        recommender = TradeRecommender()

        # Higher edge should give higher score
        score_low = recommender._calc_score(0.05, 0.05, 2.0)
        score_high = recommender._calc_score(0.15, 0.15, 2.0)
        assert score_high > score_low

        # Odds sweetspot bonus
        score_sweetspot = recommender._calc_score(0.10, 0.10, 2.5)
        score_extreme = recommender._calc_score(0.10, 0.10, 8.0)
        assert score_sweetspot > score_extreme

    def test_recommend_returns_sorted(self, sample_upcoming_df):
        """Test recommendations are sorted by score."""
        config = TradeConfig(min_edge=0.01, min_score=0.01)
        recommender = TradeRecommender(config)
        recs = recommender.recommend(sample_upcoming_df)

        if len(recs) > 1:
            scores = [r.score for r in recs]
            assert scores == sorted(scores, reverse=True)

    def test_recommend_respects_top_n(self, sample_upcoming_df):
        """Test top_n limit is respected."""
        config = TradeConfig(min_edge=0.01, min_score=0.01, top_n=2)
        recommender = TradeRecommender(config)
        recs = recommender.recommend(sample_upcoming_df)
        assert len(recs) <= 2

    def test_recommend_filters_by_edge(self, sample_upcoming_df):
        """Test minimum edge filter works."""
        # Very high edge requirement should filter most
        config = TradeConfig(min_edge=0.50)
        recommender = TradeRecommender(config)
        recs = recommender.recommend(sample_upcoming_df)
        assert len(recs) == 0 or all(r.edge >= 0.50 for r in recs)

    def test_recommend_filters_by_odds(self, sample_upcoming_df):
        """Test odds range filter works."""
        config = TradeConfig(min_odds=3.0, max_odds=4.0, min_edge=0.01)
        recommender = TradeRecommender(config)
        recs = recommender.recommend(sample_upcoming_df)
        for r in recs:
            assert 3.0 <= r.odds <= 4.0


class TestTradeRecommendation:
    """Test TradeRecommendation dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        rec = TradeRecommendation(
            match_key="2024-12-15_E0_Arsenal_Chelsea",
            date="2024-12-15",
            time="15:00",
            division="E0",
            home_team="Arsenal",
            away_team="Chelsea",
            side="H",
            odds=2.5,
            model_confidence=0.65,
            implied_prob=0.40,
            edge=0.25,
            ev=0.375,
            score=0.30,
            stake=5.0,
            stake_pct=0.05,
            rationale={"summary": "test"}
        )
        d = rec.to_dict()
        assert d["match_key"] == "2024-12-15_E0_Arsenal_Chelsea"
        assert d["side"] == "H"
        assert d["odds"] == 2.5
        assert d["stake"] == 5.0


class TestExplainability:
    """Test SHAP extraction and rationale generation."""

    def test_extract_shap_drivers(self, sample_upcoming_df):
        """Test SHAP feature extraction."""
        recommender = TradeRecommender()
        row = sample_upcoming_df.iloc[0]
        drivers = recommender._extract_shap_drivers(row)

        assert isinstance(drivers, dict)
        # Should have extracted SHAP features
        if drivers:
            assert 'FEATURE_A' in drivers or 'FEATURE_B' in drivers

    def test_generate_rationale(self, sample_upcoming_df):
        """Test rationale generation."""
        recommender = TradeRecommender()
        row = sample_upcoming_df.iloc[0]
        rationale = recommender._generate_rationale(
            row, "H", 0.65, 0.40, 0.25
        )

        assert "summary" in rationale
        assert "bullets" in rationale
        assert len(rationale["bullets"]) >= 2

    def test_rationale_without_shap(self):
        """Test rationale degrades gracefully without SHAP."""
        df = pd.DataFrame({
            'F_DATE': [pd.to_datetime('2024-12-15')],
            'F_TIME': ['15:00'],
            'F_DIV': ['E0'],
            'F_H_TEAM': ['Arsenal'],
            'F_A_TEAM': ['Chelsea'],
            'PRED_RESULT_NUM': [1.0],
            'PRED_DIFF': [1.5],
        })
        recommender = TradeRecommender()
        row = df.iloc[0]
        rationale = recommender._generate_rationale(
            row, "H", 0.65, 0.40, 0.25
        )

        # Should still have summary and bullets
        assert "summary" in rationale
        assert "bullets" in rationale
        # SHAP drivers should be empty
        assert rationale.get("shap_drivers", {}) == {}


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_get_recommended_trades(self, sample_upcoming_df):
        """Test the convenience function works."""
        config = TradeConfig(min_edge=0.01, min_score=0.01)
        trades = get_recommended_trades(sample_upcoming_df, config)
        assert isinstance(trades, list)
        for t in trades:
            assert isinstance(t, TradeRecommendation)

    def test_get_recommended_trades_empty(self, sample_completed_df):
        """Test with no upcoming matches."""
        trades = get_recommended_trades(sample_completed_df)
        assert trades == []
