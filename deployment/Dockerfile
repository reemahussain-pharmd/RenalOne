FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Streamlit config
RUN mkdir -p ~/.streamlit && echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
[theme]\n\
primaryColor = '#2980b9'\n\
backgroundColor = '#f7fafc'\n\
secondaryBackgroundColor = '#ffffff'\n\
textColor = '#1e3a5f'\n\
" > ~/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
