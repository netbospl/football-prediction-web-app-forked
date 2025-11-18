from datetime import datetime
import os
from typing import Optional


def _get_env(name: str, *, default: Optional[str] = None, required: bool = False) -> str:
    """
    Read an environment variable, optionally enforcing that it is present.

    :param name: Name of the environment variable.
    :param default: Default value to use when not required or missing.
    :param required: When True, raise a RuntimeError if the variable is unset/empty.
    """
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(
            f"Missing required environment variable '{name}'. "
            "Set it in your environment or .env file before running the app."
        )
    return value


class Config:
    # External data source
    FOOTBALL_DATA_URL = _get_env(
        "FOOTBALL_DATA_URL",
        default="https://www.football-data.co.uk",
        required=False,
    )
    FOOTBALL_DATA_TABLE = _get_env(
        "FOOTBALL_DATA_TABLE",
        default="mmz4281",
        required=False,
    )

    # Predictions source (Azure or local file)
    PREDICTIONS_SOURCE = _get_env(
        "PREDICTIONS_SOURCE",
        default="azure",
        required=False,
    )
    PREDICTIONS_LOCAL_PATH = _get_env(
        "PREDICTIONS_LOCAL_PATH",
        default="data/predictions_valid.parquet",
        required=False,
    )

    _REQUIRE_AZURE = PREDICTIONS_SOURCE.lower() != "local"

    # Azure access
    AZURE_CONNECTION_STRING = _get_env(
        "AZURE_CONNECTION_STRING",
        required=_REQUIRE_AZURE,
    )
    AZURE_CONTAINER_NAME = _get_env(
        "AZURE_CONTAINER_NAME",
        required=_REQUIRE_AZURE,
    )
    AZURE_RESULTS_TABLE = "results"
    AZURE_FIXTURES_TABLE = "fixtures"
    AZURE_PROCESSED_TABLE = "processed"
    AZURE_PREDICTIONS_TABLE = "predictions"
    AZURE_MODELS_FOLDER = "models"

    # Local file paths
    PREDICTED_FPATH = _get_env(
        "PREDICTED_FPATH",
        default="static/predicted.txt",
        required=False,
    )

    # starting year for each league
    LEAGUES = {"E0": 5,
               "D1": 6,
               "I1": 5,
               "SP1": 5,
               "F1": 5,
               "E1": 5,
               "P1": 17,
               "N1": 17,
               "T1": 17,
               "B1": 17}

    # First and last season (starting year).
    # For current year, get current year and subtract 1 if current month is June or lower.
    # So long as something like covid does not happen again, this assumption should hold.
    FIRST_SEASON = 5
    CURRENT_SEASON = (datetime.now().year - 2000) - (datetime.now().month <= 6)

    # column mapping
    TARGET_COL = "F_H_DIFF"
    COL_MAPPING = {"Div": "F_DIV",
                   "Date": "F_DATE",
                   "Time": "F_TIME",
                   "HomeTeam": "F_H_TEAM",
                   "AwayTeam": "F_A_TEAM",
                   "FTHG": "F_H_GOALS",
                   "FTAG": "F_A_GOALS",
                   "FTR": "F_RESULT",
                   "HS": "F_H_SHOTS",
                   "AS": "F_A_SHOTS",
                   "HST": "F_H_TSHOTS",
                   "AST": "F_A_TSHOTS",
                   "HF": "F_H_FOULS",
                   "AF": "F_A_FOULS",
                   "HC": "F_H_CORNERS",
                   "AC": "F_A_CORNERS",
                   "HY": "F_H_YELLOWS",
                   "AY": "F_A_YELLOWS",
                   "HR": "F_H_REDS",
                   "AR": "F_A_REDS",
                   "BbMxH": "ODDS_H_MAX",
                   "BbMxD": "ODDS_D_MAX",
                   "BbMxA": "ODDS_A_MAX",
                   "MaxH": "ODDS_H_MAX",
                   "MaxD": "ODDS_D_MAX",
                   "MaxA": "ODDS_A_MAX",
                   "BbAvH": "ODDS_H_AVG",
                   "BbAvD": "ODDS_D_AVG",
                   "BbAvA": "ODDS_A_AVG",
                   "AvgH": "ODDS_H_AVG",
                   "AvgD": "ODDS_D_AVG",
                   "AvgA": "ODDS_A_AVG"}

    PRED_MAPPING = {1.0: "H",
                    0.0: "D",
                   -1.0: "A"}
