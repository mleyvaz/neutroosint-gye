FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8503

CMD ["streamlit", "run", "src/dashboard.py", \
     "--server.port=8503", "--server.headless=true", \
     "--server.enableCORS=false"]
