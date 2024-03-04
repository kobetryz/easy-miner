FROM python:3.11-slim

WORKDIR /app

COPY /server /app

COPY /cloud_scripts /app

RUN chmod +x /app/update_miner-25.sh
RUN chmod +x /app/update_miner-1.sh
RUN chmod +x /app/update_miner-13.sh
RUN chmod +x /app/update_miner-20.sh

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
