# 🧾 Data Sources Description

All raw data is located under:  
`/dataset/HS500-samples/`

## 📄 News (JSONL)
- Location: `/dataset/HS500-samples/SP500_news/AA.jsonl` (also AAAU, AACG)
- Format:
  - One JSON object per line (JSONL format)
  - Fields include:
    - `Date`: Publication date of the news article (format may vary)
    - `Article`: Full text of the news article
    - `Article_title`: Title or headline of the article
    - `Stock_symbol`: Ticker symbol associated with the article
- Example (JSONL snippet):
  ```json
  {"Date": "2022-01-15", "Article": "Company AA reported record earnings...", "Article_title": "AA Reports Record Earnings", "Stock_symbol": "AA"}
  {"Date": "2022-01-16", "Article": "AA faces new regulatory challenges...", "Article_title": "Regulatory Hurdles for AA", "Stock_symbol": "AA"}
  ```
- Usage in Project:
  - Provides unstructured textual data for each S&P 500 company, enabling:
    - Sentiment analysis and extraction of news-based features
    - Event detection and correlation with market movements
    - Augmenting other data modalities (e.g., combining news sentiment with financials)
  - Data is loaded and preprocessed by dedicated loaders in `backend/data_loader/`, which handle parsing, date normalization, and text cleaning as needed.
  - Expert modules in `backend/experts/` can access the news data for tasks such as natural language processing, feature engineering, or as part of multi-modal models.
- Notes:
  - Coverage is sparse and publication dates may be irregular or in varying formats.
  - Each file is named after the ticker symbol it covers (e.g., `AA.jsonl` for ticker AA).
  - Articles may vary in length and relevance; preprocessing may include filtering or deduplication steps.

## 🖼️ Chart Images
- Location: `/dataset/HS500-samples/SP500_images/<ticker>/`
- Format:
  - Each subfolder is named after a stock ticker (e.g., `aa`, `aaau`, `aacg`).
  - Files are named using the pattern: `<ticker>_<year>_<H1/H2>_candlestick.png`
    - Example: `aa_2000_H1_candlestick.png` (first half of 2000 for ticker AA)
    - There are two images per year per ticker: one for H1 (first half) and one for H2 (second half).
- Usage in Project:
  - Provides visual representations of stock price movements (candlestick charts) for each company and period.
  - Enables:
    - Computer vision tasks such as image classification, pattern recognition, or feature extraction from chart images.
    - Multi-modal modeling by combining visual features with tabular, time series, or news data.
    - Human inspection or visualization of historical price trends.
  - Data is loaded and preprocessed by dedicated loaders in `backend/data_loader/`, which can handle image reading, resizing, normalization, and conversion to tensors as needed for downstream models.
  - Expert modules in `backend/experts/` can access the image data for tasks such as deep learning, technical pattern detection, or as part of multi-modal pipelines.
- Notes:
  - Image coverage is limited to two periods per year per ticker (H1 and H2).
  - Image quality, size, and format are consistent (PNG), but preprocessing may be required for model input.
  - The modular data loader design allows for easy extension to additional image types or periods if needed.

## 📈 Time Series (CSV)
- Location: `/dataset/HS500-samples/SP500_time_series/aa.csv` (also for aaau, aacg)
- Format:
  - Each file is named after a stock ticker (e.g., `aa.csv`, `aaau.csv`, `aacg.csv`).
  - CSV columns: `Date,Open,High,Low,Close,Volume,Dividends,Stock Splits`
  - Example (CSV snippet):
    ```csv
    Date,Open,High,Low,Close,Volume,Dividends,Stock Splits
    2022-01-03,50.12,51.00,49.80,50.85,1234567,0.00,0
    2022-01-04,50.90,52.10,50.50,51.95,2345678,0.00,0
    ...
    ```
- Usage in Project:
  - Provides daily historical price and volume data for each S&P 500 company.
  - Enables:
    - Time series analysis, forecasting, and anomaly detection.
    - Feature engineering for machine learning models (e.g., returns, volatility, moving averages).
    - Correlation studies and event-based analysis (e.g., linking news or fundamentals to price movements).
  - Data is loaded and preprocessed by dedicated loaders in `backend/data_loader/`, which handle parsing, date alignment, missing value imputation, and feature extraction as needed.
  - Expert modules in `backend/experts/` can access the time series data for tasks such as prediction, clustering, or as part of multi-modal pipelines.
- Notes:
  - Data is daily frequency, typically covering the early 2000s to present (depending on ticker).
  - Some tickers may have missing dates or incomplete records; loaders include logic for handling gaps.
  - The modular loader design allows for easy extension to additional tickers or time frequencies if needed.

## 📊 Fundamental Data (JSON)
- Location: `/dataset/HS500-samples/SP500_tabular/<ticker>/`
- Files:
  - `condensed_consolidated_balance_sheets.json`
  - `condensed_consolidated_statement_of_cash_flows.json`
  - `condensed_consolidated_statement_of_equity.json`
- Structure:
  - Each file contains a list of JSON objects, each representing a financial statement snapshot for a specific period (typically annual or quarterly).
  - The keys correspond to standard financial statement line items (e.g., `total_assets`, `net_income`, `cash_and_cash_equivalents`).
  - Example (balance sheet JSON snippet):
    ```json
    [
      {
        "date": "2022-12-31",
        "total_assets": 123456789,
        "total_liabilities": 98765432,
        "shareholder_equity": 24691357,
        ...
      },
      ...
    ]
    ```
- Usage in Project:
  - These files provide fundamental financial data for each S&P 500 company (by ticker), enabling:
    - Extraction of financial ratios and features for quantitative analysis.
    - Input features for machine learning models (e.g., for prediction, classification, or clustering tasks).
    - Comparative analysis of company fundamentals across time or between companies.
  - Data is loaded and preprocessed by dedicated loaders in `backend/data_loader/`, which standardize and prepare the data for downstream expert modules in `backend/experts/`.
  - The modular design allows each expert to access only the relevant modality (e.g., tabular, time series, news, or images) as needed for its task.
- Notes:
  - The data is organized by ticker symbol, with each subfolder containing the three statement types for that company.
  - Statement formats and available fields may vary slightly between companies or over time, so loaders include logic for handling missing or extra fields.

Each expert module in `backend/experts/` loads its specific data modality using loaders in `backend/data_loader/`.
