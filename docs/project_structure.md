moe_trader/
├── backend/
│   ├── core/
│   │   ├── config.py
│   │   ├── enums.py
│   │   └── date_utils.py
│   ├── data_loader/                     # Loaders for each data type
│   │   ├── load_news.py
│   │   ├── load_charts.py
│   │   ├── load_fundamentals.py
│   │   └── load_prices.py
│   ├── experts/
│   │   ├── sentiment_expert.py
│   │   ├── technical_timeseries_expert.py
│   │   ├── technical_chart_expert.py
│   │   └── fundamental_expert.py
│   ├── gating/
│   │   └── gating_network.py
│   ├── aggregation/
│   │   └── aggregator.py
│   ├── inference/
│   │   └── run_daily_inference.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── backtester.py
│   ├── requirements.txt
│   └── README.md
│
├── dataset/
│   └── HS500-samples/
│       ├── SP500_images/
│       │   ├── aa/
│       │   │   └── aa_2000_H1_candlestick.png
│       │   ├── aaau/
│       │   └── aacg/
│       ├── SP500_news/
│       │   ├── AA.jsonl
│       │   ├── AAAU.jsonl
│       │   └── AACG.jsonl
│       ├── SP500_tabular/
│       │   ├── aa/
│       │   │   ├── condensed_consolidated_balance_sheets.json
│       │   ├── aaau/
│       │   └── aacg/
│       └── SP500_time_series/
│           ├── aa.csv
│           ├── aaau.csv
│           └── aacg.csv
│
├── notebooks/
│   ├── data_exploration.ipynb
│   └── chart_embedding_experiments.ipynb
│
├── frontend/
│   ├── app.py
│   └── components/
│       └── charts.py
│
└── docs/
    ├── CURSOR_GUIDE.md
    ├── SYSTEM_OVERVIEW.md
    ├── DATA_DESCRIPTION.md
    └── MODELS_AND_ROUTING.md
