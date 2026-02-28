# Technical Steering: Local Databricks/AWS Mock

## Tech Stack

**Language:** Python 3.10+

**Frontend Framework:** Streamlit

**Database:** SQLite (Simulating Databricks SQL Warehouse)

**AI Integration:** Amazon Bedrock via `strands sdk`. Use model 'global.anthropic.claude-sonnet-4-6'

**Python and PIP:** Use python3 and pip3 when you need to use Python and PIP commands

## Architectural Constraints

**Separation of Concerns:** Keep the Streamlit UI logic (`app.py`) completely separate from the database connection logic and the AI logic.

**Data Protection:** Use parameterized SQL queries where possible, and never hardcode AWS credentials or database paths. Use a `.env` file or `st.secrets`.

**File Paths:** Always use `pathlib` for robust path resolution.