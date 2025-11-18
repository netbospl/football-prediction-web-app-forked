import math
import os

import pandas as pd
import pytest


def _ensure_env():
    """
    Config in src.utils.config reads AZURE_* on import.
    Set dummy values so frontend modules can be imported safely.
    """
    os.environ.setdefault("AZURE_CONNECTION_STRING", "test-connection-string")
    os.environ.setdefault("AZURE_CONTAINER_NAME", "test-container")


def test_nullable_pct_basic():
    _ensure_env()
    from src.frontend import metrics

    assert metrics.nullable_pct(50, 100) == 50
    assert metrics.nullable_pct(0, 10) == 0


def test_nullable_pct_zero_denominator_raises():
    _ensure_env()
    from src.frontend import metrics

    with pytest.raises(ZeroDivisionError):
        metrics.nullable_pct(10, 0)


@pytest.mark.parametrize(
    "value,expected",
    [
        (50, "50.0%"),
        (0, "0.0%"),
        (12.345, "12.3%"),
        (math.nan, "0.0%"),
    ],
)
def test_format_pct_formats_and_handles_nan(value, expected):
    _ensure_env()
    from src.frontend import metrics

    assert metrics.format_pct(value) == expected


def test_get_metrics_without_formatting_keeps_numeric_types():
    _ensure_env()
    from src.frontend import metrics

    df = pd.DataFrame(
        {
            "F_H_GAMES": [10, 20],
            "PRED_CORRECT": [7, 10],
            "PRED_RETURNS": [3.5, -2.0],
        }
    )

    out = metrics.get_metrics(df.copy(), fmt=False)

    # New columns should be present and numeric
    assert list(out.columns) == [
        "F_H_GAMES",
        "PRED_CORRECT",
        "PRED_RETURNS",
        "Finished Games",
        "Accuracy (%)",
        "ROI (%)",
    ]

    assert out["Finished Games"].dtype.kind in {"i", "u", "f"}
    assert out["Accuracy (%)"].dtype.kind in {"i", "u", "f"}
    assert out["ROI (%)"].dtype.kind in {"i", "u", "f"}

    # Spot-check values
    assert out.loc[0, "Finished Games"] == 10
    pytest.approx(out.loc[0, "Accuracy (%)"], rel=1e-6) == 70.0
    pytest.approx(out.loc[1, "ROI (%)"], rel=1e-6) == (-2.0 / 20) * 100


def test_get_metrics_with_formatting_returns_strings():
    _ensure_env()
    from src.frontend import metrics

    df = pd.DataFrame(
        {
            "F_H_GAMES": [10],
            "PRED_CORRECT": [7],
            "PRED_RETURNS": [3.5],
        }
    )

    out = metrics.get_metrics(df.copy(), fmt=True)

    # Formatted columns should be strings with percent sign
    assert out.loc[0, "Finished Games"] == "10"
    assert isinstance(out.loc[0, "Finished Games"], str)

    assert out.loc[0, "Accuracy (%)"].endswith("%")
    assert out.loc[0, "ROI (%)"].endswith("%")

