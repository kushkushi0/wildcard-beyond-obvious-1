# WILDCARD: BEYOND THE OBVIOUS

A beginner-friendly Streamlit prototype for CSV-based risk signal exploration.

## Features
- Dashboard with high/medium/low risk counts and charts
- CSV upload
- Risk Analysis table with filters
- Early Warnings with reasons and suggested review actions
- Downloadable CSV report
- Synthetic sample data built into the app

> **Important:** This prototype uses transparent demonstration rules, not a trained AI model. Risk labels are not proof of fraud or validated predictions. Do not upload private or sensitive real-world data to a public repository.

## Run on Windows
Install Python 3.10+ then open a terminal in this folder:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

If activation is blocked in PowerShell, try installing and running without activating:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal (usually http://localhost:8501).

## CSV columns
Recommended columns:
- `event_id` — optional record ID
- `transaction_amount` — numeric amount
- `failed_attempts` — non-negative count
- `unusual_activity` — 0/1 or true/false

Example:

```csv
event_id,transaction_amount,failed_attempts,unusual_activity
E001,120,0,0
E002,8500,3,1
E003,450,1,0
```

Some alternative names are accepted, such as `amount`, `failed_login_attempts`, and `unusual`.

## Upload to GitHub
1. Create a new repository named `wildcard-beyond-obvious`.
2. Extract the ZIP you downloaded.
3. Upload `app.py`, `requirements.txt`, `README.md`, `.gitignore`, and `sample_data.csv`.
4. Do **not** upload `.venv`, secrets, or private data.
5. Commit the files with a message like `Add WILDCARD risk detection prototype`.

## Optional deployment
After pushing to GitHub, you can deploy through Streamlit Community Cloud by selecting the repository and setting the main file to `app.py`.

## Limitations
- Risk scores are based on simple demonstration rules.
- The app does not connect to live systems or monitor transactions in real time.
- Validate any approach with appropriate data and domain experts before real-world use.
