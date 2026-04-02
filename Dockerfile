FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-hf.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy application code
COPY app/ ./app/
COPY config.py .
COPY app.py .

# Copy data and models
COPY data/raw_supabase_data.json ./data/
COPY models/ ./models/

# Create data directory if it doesn't exist
RUN mkdir -p data

ENV PORT=7860
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]