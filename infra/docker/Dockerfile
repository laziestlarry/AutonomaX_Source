
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080 8501
CMD ["/bin/bash","-lc","uvicorn apps.chatbot.main:APP --host 0.0.0.0 --port 8080 & streamlit run apps/dashboard/app.py --server.port 8501 --server.address 0.0.0.0"]
