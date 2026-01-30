"""Test explainability features including SHAP extraction."""

import pytest
import pandas as pd
import numpy as np


class TestShapExtraction:
    """Test SHAP value extraction from prediction data."""

    @pytest.fixture
    def sample_row_with_shap(self):
        """Create a sample row with SHAP columns."""
        return pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'F_DIV': 'E0',
            'F_H_TEAM': 'Arsenal',
            'F_A_TEAM': 'Chelsea',
            'PRED_DIFF': 1.5,
            'PRED_RESULT_NUM': 1.0,
            'SHAP_T_H_POINTS': 0.25,
            'SHAP_T_A_POINTS': -0.15,
            'SHAP_H_GOALS_SCORED': 0.10,
            'SHAP_A_GOALS_SCORED': 0.05,
            'SHAP_ODDS_H_MAX': -0.08,
            'SHAP_ODDS_D_MAX': 0.02,
            'SHAP_ODDS_A_MAX': 0.03,
            'SHAP_INTERCEPT': 0.5,
        })

    @pytest.fixture
    def sample_row_no_shap(self):
        """Create a sample row without SHAP columns."""
        return pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'F_DIV': 'E0',
            'F_H_TEAM': 'Arsenal',
            'F_A_TEAM': 'Chelsea',
            'PRED_DIFF': 1.5,
            'PRED_RESULT_NUM': 1.0,
        })

    def test_extract_shap_identifies_columns(self, sample_row_with_shap):
        """Test that SHAP columns are correctly identified."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        drivers = recommender._extract_shap_drivers(sample_row_with_shap)

        assert isinstance(drivers, dict)
        assert len(drivers) > 0
        # Should not include INTERCEPT
        assert 'INTERCEPT' not in drivers

    def test_extract_shap_sorts_by_magnitude(self, sample_row_with_shap):
        """Test that SHAP values are sorted by absolute value."""
        from src.trades.recommend import TradeRecommender, TradeConfig

        config = TradeConfig(top_shap_features=3)
        recommender = TradeRecommender(config)
        drivers = recommender._extract_shap_drivers(sample_row_with_shap)

        # Get absolute values
        abs_values = [abs(v) for v in drivers.values()]

        # Should be sorted descending
        assert abs_values == sorted(abs_values, reverse=True)

    def test_extract_shap_respects_top_n(self, sample_row_with_shap):
        """Test that top_n limit is respected."""
        from src.trades.recommend import TradeRecommender, TradeConfig

        config = TradeConfig(top_shap_features=3)
        recommender = TradeRecommender(config)
        drivers = recommender._extract_shap_drivers(sample_row_with_shap)

        assert len(drivers) <= 3

    def test_extract_shap_handles_missing(self, sample_row_no_shap):
        """Test graceful handling when no SHAP columns exist."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        drivers = recommender._extract_shap_drivers(sample_row_no_shap)

        assert drivers == {}

    def test_extract_shap_ignores_zero_values(self):
        """Test that zero SHAP values are excluded."""
        from src.trades.recommend import TradeRecommender

        row = pd.Series({
            'SHAP_FEATURE_A': 0.25,
            'SHAP_FEATURE_B': 0.0,  # Should be excluded
            'SHAP_FEATURE_C': -0.15,
            'SHAP_INTERCEPT': 0.5,
        })

        recommender = TradeRecommender()
        drivers = recommender._extract_shap_drivers(row)

        assert 'FEATURE_A' in drivers
        assert 'FEATURE_C' in drivers
        assert 'FEATURE_B' not in drivers

    def test_extract_shap_ignores_nan_values(self):
        """Test that NaN SHAP values are excluded."""
        from src.trades.recommend import TradeRecommender

        row = pd.Series({
            'SHAP_FEATURE_A': 0.25,
            'SHAP_FEATURE_B': np.nan,  # Should be excluded
            'SHAP_FEATURE_C': -0.15,
            'SHAP_INTERCEPT': 0.5,
        })

        recommender = TradeRecommender()
        drivers = recommender._extract_shap_drivers(row)

        assert 'FEATURE_A' in drivers
        assert 'FEATURE_C' in drivers
        assert 'FEATURE_B' not in drivers


class TestRationale:
    """Test rationale generation."""

    @pytest.fixture
    def sample_row(self):
        """Create sample row for rationale tests."""
        return pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'F_DIV': 'E0',
            'F_H_TEAM': 'Arsenal',
            'F_A_TEAM': 'Chelsea',
            'PRED_DIFF': 1.5,
            'SHAP_HOME_FORM': 0.30,
            'SHAP_AWAY_FORM': -0.20,
            'SHAP_HEAD_TO_HEAD': 0.15,
            'SHAP_INTERCEPT': 0.5,
        })

    def test_rationale_has_summary(self, sample_row):
        """Test rationale includes summary line."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        rationale = recommender._generate_rationale(
            sample_row, "H", 0.65, 0.40, 0.25
        )

        assert 'summary' in rationale
        assert isinstance(rationale['summary'], str)
        assert len(rationale['summary']) > 0

    def test_rationale_has_bullets(self, sample_row):
        """Test rationale includes bullet points."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        rationale = recommender._generate_rationale(
            sample_row, "H", 0.65, 0.40, 0.25
        )

        assert 'bullets' in rationale
        assert isinstance(rationale['bullets'], list)
        assert len(rationale['bullets']) >= 2

    def test_rationale_includes_probabilities(self, sample_row):
        """Test rationale mentions probability comparison."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        rationale = recommender._generate_rationale(
            sample_row, "H", 0.65, 0.40, 0.25
        )

        bullets = rationale['bullets']
        prob_mentioned = any('65' in b or '40' in b for b in bullets)
        assert prob_mentioned

    def test_rationale_includes_shap_drivers(self, sample_row):
        """Test rationale includes SHAP-based explanations."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        rationale = recommender._generate_rationale(
            sample_row, "H", 0.65, 0.40, 0.25
        )

        assert 'shap_drivers' in rationale
        if rationale['shap_drivers']:
            # Should have at least one driver
            assert len(rationale['shap_drivers']) > 0

    def test_summary_format(self, sample_row):
        """Test summary format is correct."""
        from src.trades.recommend import TradeRecommender

        recommender = TradeRecommender()
        rationale = recommender._generate_rationale(
            sample_row, "H", 0.65, 0.40, 0.25
        )

        summary = rationale['summary']
        # Should contain key elements
        assert 'Home' in summary
        assert 'model' in summary.lower()
        assert 'market' in summary.lower()
        assert 'edge' in summary.lower()


class TestDBShapExtraction:
    """Test SHAP extraction for database storage."""

    def test_db_client_extracts_top_shap(self):
        """Test the DB client SHAP extraction function."""
        from src.db.client import _extract_top_shap

        row = pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'SHAP_FEATURE_A': 0.50,
            'SHAP_FEATURE_B': 0.30,
            'SHAP_FEATURE_C': -0.25,
            'SHAP_FEATURE_D': 0.10,
            'SHAP_FEATURE_E': 0.05,
            'SHAP_FEATURE_F': 0.02,
            'SHAP_INTERCEPT': 0.5,
        })

        result = _extract_top_shap(row, top_n=3)

        assert isinstance(result, dict)
        assert len(result) <= 3

        # Top 3 by absolute value should be A, B, C
        assert 'FEATURE_A' in result
        assert 'FEATURE_B' in result
        assert 'FEATURE_C' in result

    def test_db_client_handles_empty_shap(self):
        """Test DB client handles rows without SHAP columns."""
        from src.db.client import _extract_top_shap

        row = pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'F_DIV': 'E0',
        })

        result = _extract_top_shap(row)
        assert result == {}

    def test_db_client_rounds_values(self):
        """Test SHAP values are rounded for storage."""
        from src.db.client import _extract_top_shap

        row = pd.Series({
            'SHAP_FEATURE_A': 0.123456789,
            'SHAP_INTERCEPT': 0.5,
        })

        result = _extract_top_shap(row)

        # Value should be rounded to 4 decimal places
        if 'FEATURE_A' in result:
            assert result['FEATURE_A'] == 0.1235


class TestMatchKeyGeneration:
    """Test match key generation for DB storage."""

    def test_match_key_format(self):
        """Test match key has expected format."""
        from src.db.client import _make_match_key

        row = pd.Series({
            'F_DATE': pd.to_datetime('2024-12-15'),
            'F_DIV': 'E0',
            'F_H_TEAM': 'Arsenal',
            'F_A_TEAM': 'Chelsea',
        })

        key = _make_match_key(row)

        assert '2024-12-15' in key
        assert 'E0' in key
        assert 'Arsenal' in key
        assert 'Chelsea' in key
        assert key.count('_') == 3

    def test_match_key_handles_string_date(self):
        """Test match key works with string dates."""
        from src.db.client import _make_match_key

        row = pd.Series({
            'F_DATE': '2024-12-15',
            'F_DIV': 'E0',
            'F_H_TEAM': 'Arsenal',
            'F_A_TEAM': 'Chelsea',
        })

        key = _make_match_key(row)
        assert '2024-12-15' in key
