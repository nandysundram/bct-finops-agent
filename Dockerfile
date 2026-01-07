FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (if needed for some packages)
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Streamlit server config
ENV PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true
EXPOSE 8080

CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0"]
