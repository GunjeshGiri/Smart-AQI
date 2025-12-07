# src/train.py
# Baseline LightGBM time-series training with simple TimeSeriesSplit cross-validation
import argparse
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import joblib
import os

def train(data_path, target='value', model_out='models/lgb_baseline.pkl'):
    df = pd.read_parquet(data_path)
    # simple dropna
    df = df.dropna(subset=[target])
    features = [c for c in df.columns if c not in ['datetime','location',target]]
    # convert category
    if 'location' in df.columns:
        df['location_code'] = df['location'].astype('category').cat.codes
        features.append('location_code')
    X = df[features]
    y = df[target]
    tscv = TimeSeriesSplit(n_splits=3)
    maes = []
    models = []
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        dtrain = lgb.Dataset(X_train, y_train)
        dval = lgb.Dataset(X_val, y_val, reference=dtrain)
        params = {'objective':'regression','metric':'mae','verbosity':-1}
        bst = lgb.train(params, dtrain, valid_sets=[dval], early_stopping_rounds=50, num_boost_round=1000)
        preds = bst.predict(X_val)
        mae = mean_absolute_error(y_val, preds)
        maes.append(mae)
        models.append(bst)
    print("CV MAE:", sum(maes)/len(maes))
    os.makedirs(os.path.dirname(model_out), exist_ok=True)
    joblib.dump(models[-1], model_out)
    print("Saved model to", model_out)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--target', default='value')
    parser.add_argument('--out', default='models/lgb_baseline.pkl')
    args = parser.parse_args()
    train(args.data, args.target, args.out)
