# Smart-AQI — Smart City AQI Prediction & Health Risk Alert System

## Project overview
End-to-end system to ingest air-quality and weather data, train forecasting models, expose predictions via an API,
and provide a dashboard plus alerting (SMS/WhatsApp/email).

## What is included in this scaffold
- `data/` - target for raw & processed data (empty in scaffold)
- `notebooks/` - suggested place for EDA and experiments
- `src/` - application code (ingest, etl, features, train, model, api, dashboard)
- `docker/` - docker files and docker-compose
- `deployment/` - CI/CD / GitHub Actions example
- `requirements.txt` - Python deps to install
- `docker-compose.yml` - to run API + dashboard locally
- `README.md` - this file

## Quickstart (local)
1. Create a Python venv and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows PowerShell
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Download data:
   - Use `src/ingest.py` to fetch from OpenAQ or CPCB (you need internet keys where required).
   - Example: `python src/ingest.py --city "New Delhi" --parameter pm25 --limit 10000`
4. Process data and create features:
   ```bash
   python src/etl.py --input data/raw/openaq_delhi_pm25.parquet --output data/processed/features.parquet
   ```
5. Train baseline model (LightGBM):
   ```bash
   python src/train.py --data data/processed/features.parquet --target pm25
   ```
6. Run API and dashboard with Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Next steps (suggested)
- Implement advanced DL models (LSTM / Transformer) in `src/model/`
- Add scheduler (Airflow / GitHub Actions) for periodic retraining
- Integrate Twilio / WhatsApp for alerts in `src/alerts.py`
- Add monitoring (MLflow / Prometheus) and model registry

## References
- OpenAQ API (https://openaq.org)
- CPCB / India national AQI
- WHO Air Quality Guidelines
