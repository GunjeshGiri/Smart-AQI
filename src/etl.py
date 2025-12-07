# src/etl.py
# Minimal ETL pipeline: load raw parquet, basic cleaning, feature engineering, save processed parquet
import argparse
import pandas as pd
import os
def run(input_path, output_path):
    df = pd.read_parquet(input_path)
    # basic normalizations
    if 'date.utc' in df.columns:
        df['datetime'] = pd.to_datetime(df['date.utc'])
    elif 'date.local' in df.columns:
        df['datetime'] = pd.to_datetime(df['date.local'])
    else:
        # try common columns
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        else:
            raise ValueError("No datetime column found in raw data.")
    df = df.sort_values('datetime')
    # resample to hourly by station + parameter
    df = df.set_index('datetime')
    # aggregate to hourly mean per location
    hourly = df.groupby(['location']).resample('1H').mean().reset_index()
    # feature engineering: rolling means and lags per location
    hourly['hour'] = hourly['datetime'].dt.hour
    hourly['dayofweek'] = hourly['datetime'].dt.dayofweek
    hourly['rolling_3h'] = hourly.groupby('location')['value'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    hourly['lag_24h'] = hourly.groupby('location')['value'].shift(24)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    hourly.to_parquet(output_path)
    print("Saved processed features to", output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='data/processed/features.parquet')
    args = parser.parse_args()
    run(args.input, args.output)
