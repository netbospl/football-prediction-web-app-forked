import os
import sys
from datetime import datetime

import pandas as pd
from xgboost import XGBRegressor

from ..explain.shap import get_shap_explanations
from ..preprocess.features import SeasonProcessor
from ..storage.tables import LocalBlobTable, ExternalBlobTable
from ..utils.functions import get_partitions, clean_results, split_features_target, enrich_df_with_predictions
from ..utils.config import Config as cfg


def refresh_fixtures():
    ex_table = ExternalBlobTable(table_name="")
    local_table = LocalBlobTable(cfg.AZURE_FIXTURES_TABLE)

    partitions = [cfg.AZURE_FIXTURES_TABLE]
    fixtures = ex_table.download(partitions, concat=False)
    local_table.upload(fixtures)

def refresh_results(partitions):
    ex_table = ExternalBlobTable(cfg.FOOTBALL_DATA_TABLE)
    local_table = LocalBlobTable(cfg.AZURE_RESULTS_TABLE)

    results = ex_table.download(partitions, concat=False)
    local_table.upload(results)

def preprocess_results(partitions, output_partition_name, add_fixtures=False):
    res_table = LocalBlobTable(cfg.AZURE_RESULTS_TABLE)
    fix_table = LocalBlobTable(cfg.AZURE_FIXTURES_TABLE)

    res = res_table.download(partitions, concat=False)
    if add_fixtures:
        fix = fix_table.download([cfg.AZURE_FIXTURES_TABLE], concat=True)

    dfs = []
    for p, df in res.items():
        if add_fixtures:
            div = p.split("/")[-1]
            df = pd.concat([df, fix.query(f"Div == '{div}'")]).reset_index(drop=True)

        df = clean_results(df)
        df = SeasonProcessor(df).run()
        dfs.append(df)
        print(datetime.now(), f"processed: {p}")

    local_table = LocalBlobTable(cfg.AZURE_PROCESSED_TABLE)
    local_table.upload({output_partition_name: pd.concat(dfs)})


def _load_or_train_model(train_data):
    model_table = LocalBlobTable(table_name=cfg.AZURE_MODELS_FOLDER, ftype="pkl")
    try:
        model = model_table.download(["model"])["model"]
    except FileNotFoundError:
        X_train, y_train = split_features_target(train_data)
        model = XGBRegressor(objective="reg:squarederror", seed=1)
        model.fit(X_train, y_train)
        model_table.upload({"model": model})
    return model


def generate_predictions(table_name, train_table_name="train"):
    processed_table = LocalBlobTable(cfg.AZURE_PROCESSED_TABLE)
    train_data = processed_table.download([train_table_name], concat=True)
    data = processed_table.download([table_name], concat=True)

    model = _load_or_train_model(train_data)

    # generate prediction
    X_data, y_data = split_features_target(data)
    pred = model.predict(X_data)
    data = enrich_df_with_predictions(data, pred)

    # add shap values
    shap_values = get_shap_explanations(X_data, model)
    data = pd.merge(data, shap_values, left_index=True, right_index=True)

    local_table = LocalBlobTable(cfg.AZURE_PREDICTIONS_TABLE, ftype="parquet")
    local_table.upload({"data": data})
