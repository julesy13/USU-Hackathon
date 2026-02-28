# Project Structure

Follow this exact directory structure for the application:

```
/
├── app.py                 # Main Streamlit entry point
├── database/
│   ├── setup_db.py        # Script to create SQLite mock tables and insert seed data
│   └── warehouse.db       # The SQLite database file (generated)
├── services/
│   ├── ai_service.py      # Handles AWS Bedrock / LLM logic to convert Text-to-SQL
│   └── db_service.py      # Handles executing SQL against SQLite
├── logs/
│   └── audit_trail.csv    # The governance log (generated)
└── requirements.txt       # Python dependencies
```