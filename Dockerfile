FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run data generation and pipeline, then start Streamlit
CMD ["sh", "-c", "python python/pipeline.py && streamlit run app/app.py --server.port=8501 --server.address=0.0.0.0"]
