# Mobile Money Fraud Detection — Standard Bank / DSC Digital Innovation Hackathon

A fraud detection system built on 636K+ mobile-money transactions, tackling a severe class-imbalance problem (0.13% fraud rate) with a full pipeline from EDA through model comparison to a deployable, interpretable rule engine.

![PowerBI Dashboard](PowerBI%20Dashboard%20Screenshot.png)

## Problem

Fraudulent mobile-money transactions cause direct financial loss and erode customer trust — but they're rare. In this dataset, only 849 of 636,262 transactions (0.13%) are fraudulent. A naive model predicting "not fraud" every time would be 99.8% accurate while catching zero fraud. The goal wasn't raw accuracy — it was building a system that reliably separates the rare fraud cases from legitimate activity while keeping false-alarm costs manageable.

## Approach

1. **EDA** — found fraud is confined entirely to `TRANSFER` and `CASH_OUT` transactions, is on average ~8x larger than legitimate transactions, and spikes in early-morning hours.
2. **Feature engineering** — built balance-consistency features (`errorBalanceOrig`, `errorBalanceDest`) that check whether account balance changes arithmetically match transaction amounts, plus zero-balance flags for origin/destination accounts.
3. **Multicollinearity correction** — used VIF screening (raw balance columns had VIFs as high as 410) and PCA to collapse redundant/correlated features.
4. **Feature selection** — used Mutual Information alongside correlation, since fraud follows threshold/interaction patterns that linear correlation misses.
5. **Modeling** — trained and compared 5 classifiers (Logistic Regression, Bayesian Logistic Regression via PyMC/ADVI, Decision Tree, Random Forest, XGBoost) on a stratified 80/20 split, with training-set-only undersampling (1:2 ratio) to avoid test-set leakage.
6. **Rule-based engine** — built a simple, fully interpretable 6-rule flagging system as a business-facing companion that requires no trained model.

## Results

Evaluated on a held-out, untouched test set (127,253 transactions, 170 fraud cases). PR-AUC is the more informative metric here, since ROC-AUC can look deceptively strong under extreme class imbalance:

| Model | ROC-AUC | PR-AUC | Notes |
|---|---|---|---|
| **XGBoost** | 0.9905 | **0.5941** | Best overall — 8.8% missed fraud, 2.9% false-alarm rate |
| Random Forest | 0.9879 | 0.5682 | Close second, slightly more conservative |
| Decision Tree | 0.9733 | 0.1684 | Interpretable but noticeably weaker |
| Bayesian Logistic Regression | 0.9426 | 0.0762 | Probabilistic counterpart to LR |
| Logistic Regression | 0.9432 | 0.0746 | Linear baseline |

All five models look strong on ROC-AUC (0.94+), but PR-AUC exposes a large gap — the tree ensembles substantially outperform the linear models, reinforcing that fraud in this data follows non-linear, threshold-based patterns rather than linear ones.

The rule-based engine, tuned to flag on ≥2 triggered rules, caught **100% of test-set fraud** at a 69% false-alarm rate — a useful audit/explainability layer, not a standalone production model.

**Top predictive features** (converging across XGBoost gain, Random Forest importance, Logistic Regression coefficients, and Mutual Information): `origZeroBefore`, `newbalanceOrig`, `type_TRANSFER`, `errorBalanceDest`.

## Tech Stack

- Python (pandas, scikit-learn, XGBoost, imbalanced-learn, PyMC)
- SHAP for model interpretability
- Power BI for dashboarding
- Tkinter for the demo app

## Running the Project

The notebook (`Group 8 hackathon_code .ipynb`) was developed and run on **Kaggle**, which provides the required libraries (pandas, scikit-learn, XGBoost, imbalanced-learn, PyMC, SHAP) pre-installed. To reproduce:

1. Upload the notebook to [Kaggle](https://www.kaggle.com/) or run it locally with Python 3.10+
2. If running locally, install dependencies:
    pip install pandas scikit-learn xgboost imbalanced-learn pymc shap matplotlib seaborn
3. Run all cells in order — the pipeline runs EDA → feature engineering → model training → evaluation sequentially

The Tkinter demo (`demo.py`) runs locally with just the Python standard library:
    python demo.py


## Repo Contents

| File | Description |
|---|---|
| `Group 8 hackathon_code .ipynb` | Full analysis pipeline: EDA, feature engineering, modeling |
| `Group 8 Hackathon Report .docx` | Full written report with methodology and discussion |
| `DSC Hackathon Group8 Fraud Detection Presentation.pptx` | Slide deck |
| `PowerBI Dashboard Screenshot.png` | Dashboard visualization |
| `demo.py` | Tkinter app demo |

## Demo

A lightweight Tkinter app lets you test the rule-based engine interactively — enter transaction details and get an instant risk assessment with a breakdown of which rules triggered.

![Fraud rule-based flagging demo](Demo%20Screenshot.png)

Example above: a R450,000 TRANSFER that drains the origin account and lands in a previously-empty destination account triggers 5/6 rules — flagged as **Critical** risk.

## Limitations & Next Steps

- The `errorBalanceOrig` signal is unusually clean in this synthetic dataset and should be re-validated against real transaction logs before production use.
- Classification thresholds weren't yet cost-optimized against a bank's actual false-negative/false-positive cost ratio.
- Only one undersampling ratio (1:2) was tested; sweeping others is a natural next step.

**Recommended deployment path:** XGBoost as the primary scoring model, with the rule engine retained as an explainable secondary/audit layer for regulatory reporting.

## Team

Group 8 — DSC Finance and Digital Innovation Hackathon