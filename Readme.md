# Pharmacy Sales Forecasting Dashboard

This project develops a machine learning pipeline to forecast pharmacy product sales and generate stock priority recommendations.

## Project Pipeline

1. SQL database extraction
2. Data cleaning
3. Exploratory data analysis
4. Feature engineering
5. Machine learning modeling
6. Sales prediction
7. Stock priority recommendation
8. Streamlit dashboard deployment

## Model

The best initial model is Random Forest Regressor based on MAE and WAPE evaluation.

## Dashboard Pages

- Overall Sales Dashboard
- Stock Recommendation Dashboard

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py