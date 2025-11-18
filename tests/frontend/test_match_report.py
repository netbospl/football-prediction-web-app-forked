import os
from datetime import date

import pandas as pd
import pytest


def _ensure_env():
    """
    Config in src.utils.config reads AZURE_* on import.
    Set dummy values so frontend modules can be imported safely.
    """
    os.environ.setdefault("AZURE_CONNECTION_STRING", "test-connection-string")
    os.environ.setdefault("AZURE_CONTAINER_NAME", "test-container")


def _make_base_row():
    """
    Create a minimal Series with all fields required by MatchReport
    and its subclasses' properties.
    """
    return pd.Series(
        {
            "F_DIV": "E0",
            "PRED_RETURNS": 1.5,
            "PRED_DIFF": 0.3,
            "F_RESULT": 1.0,
            "PRED_RESULT_NUM": 1.0,
            "F_DATE": date(2023, 1, 1),
            "F_TIME": "15:00",
            "F_H_TEAM": "Team A",
            "F_A_TEAM": "Team B",
            "F_H_GOALS": 2,
            "F_A_GOALS": 1,
        }
    )


def test_fixture_and_result_titles_and_scores(monkeypatch):
    _ensure_env()

    import streamlit as st

    # Avoid opening real UI; stub expander to a simple object.
    class DummyExpander:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(st, "expander", lambda *_, **__: DummyExpander())

    from src.frontend.match_report import FixtureReport, ResultReport

    row = _make_base_row()

    fixture = FixtureReport(row)
    result = ResultReport(row)

    # FixtureReport.score does not include goals
    assert fixture.score == "Team A - Team B"
    # ResultReport.score includes scoreline
    assert result.score == "Team A 2 - 1 Team B"

    assert "league: E0" in fixture.title
    assert "predicted: 0.30 (H)" in fixture.title

    assert "Return: 1.50" in result.res_detailed
    assert "result: 1.0" in result.title


def test_get_shap_table_builds_styled_table_with_expected_columns(monkeypatch):
    _ensure_env()

    import streamlit as st

    class DummyExpander:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(st, "expander", lambda *_, **__: DummyExpander())

    from src.frontend.match_report import FixtureReport

    row = _make_base_row()
    # Underlying feature values used for SHAP explanation
    row["FEATURE1"] = 10
    row["FEATURE2"] = 20

    report = FixtureReport(row)

    shap_values = {"SHAP_FEATURE1": 0.5, "SHAP_FEATURE2": -0.2}

    styler = report.get_shap_table(shap_values)

    # It should be a pandas Styler object
    from pandas.io.formats.style import Styler

    assert isinstance(styler, Styler)

    data = styler.data

    # Columns created by get_shap_table
    assert list(data.columns) == [
        "Feature name",
        "Feature value",
        "SHAP value",
        "Cumulative SHAP value",
    ]

    # Sorted in descending order by feature name
    assert list(data["Feature name"]) == ["SHAP_FEATURE2", "SHAP_FEATURE1"]
    assert list(data["Feature value"]) == [20, 10]
    assert list(data["SHAP value"]) == [-0.2, 0.5]

    # Cumulative SHAP is a running sum
    assert list(data["Cumulative SHAP value"]) == [-0.2, 0.3]


def test_get_shap_table_with_empty_input_returns_empty_table(monkeypatch):
    _ensure_env()

    import streamlit as st

    class DummyExpander:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(st, "expander", lambda *_, **__: DummyExpander())

    from src.frontend.match_report import FixtureReport

    row = _make_base_row()
    report = FixtureReport(row)

    styler = report.get_shap_table({})
    data = styler.data

    assert data.empty

