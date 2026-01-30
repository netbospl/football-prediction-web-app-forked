"""Test that all key modules can be imported successfully."""

import pytest


def test_import_config():
    """Test config module imports."""
    from src.utils.config import Config
    assert hasattr(Config, 'STORAGE_BACKEND')
    assert hasattr(Config, 'DATA_DIR')
    assert hasattr(Config, 'DB_PATH')
    assert hasattr(Config, 'use_azure')


def test_import_storage():
    """Test storage module imports."""
    from src.storage.tables import (
        BlobTable,
        LocalBlobTable,
        AzureBlobTable,
        ExternalBlobTable,
        get_storage_table
    )
    assert LocalBlobTable is not None
    assert get_storage_table is not None


def test_import_db():
    """Test database module imports."""
    from src.db import get_db, init_db, create_tables
    from src.db.client import (
        create_run,
        save_predictions,
        save_trades,
        get_trade_performance
    )
    assert get_db is not None
    assert create_run is not None


def test_import_trades():
    """Test trade recommendation module imports."""
    from src.trades import get_recommended_trades, TradeRecommender
    from src.trades.recommend import TradeConfig, TradeRecommendation
    assert TradeRecommender is not None
    assert TradeConfig is not None


def test_import_explain():
    """Test explainability module imports."""
    from src.explain.shap import get_shap_explanations
    assert get_shap_explanations is not None


def test_import_frontend():
    """Test frontend module imports."""
    from src.frontend.data import load_data, aggregate_df, aggregate_by_date
    from src.frontend.metrics import get_metrics, metric_dashboard
    from src.frontend.match_report import MatchReport, ResultReport, FixtureReport
    assert load_data is not None
    assert MatchReport is not None


def test_import_pipelines():
    """Test pipeline module imports."""
    from src.pipelines.update import (
        refresh_fixtures,
        refresh_results,
        preprocess_results,
        generate_predictions
    )
    assert refresh_fixtures is not None
    assert generate_predictions is not None


def test_import_preprocess():
    """Test preprocessing module imports."""
    from src.preprocess.features import SeasonProcessor
    assert SeasonProcessor is not None


def test_import_utils():
    """Test utility function imports."""
    from src.utils.functions import (
        get_partitions,
        split_features_target,
        enrich_df_with_predictions,
        clean_results
    )
    assert get_partitions is not None
    assert split_features_target is not None


def test_config_defaults():
    """Test that config has sensible defaults."""
    from src.utils.config import Config

    # Default should be local
    assert Config.STORAGE_BACKEND in ('local', 'azure')

    # Data dir should be 'data' by default
    assert Config.DATA_DIR == 'data' or 'data' in Config.DATA_DIR

    # DB path should be in data directory
    assert 'app.db' in Config.DB_PATH


def test_use_azure_logic():
    """Test Azure detection logic."""
    from src.utils.config import Config

    # If no Azure credentials, use_azure should return False
    if not Config.AZURE_CONNECTION_STRING or not Config.AZURE_CONTAINER_NAME:
        assert Config.use_azure() is False


def test_storage_factory():
    """Test storage factory returns correct type."""
    from src.storage.tables import get_storage_table, LocalBlobTable

    # With default config (local), should return LocalBlobTable
    table = get_storage_table("test", "csv")

    # If not using Azure, should be LocalBlobTable
    from src.utils.config import Config
    if not Config.use_azure():
        assert isinstance(table, LocalBlobTable)
