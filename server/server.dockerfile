FROM python:3.10-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY . /app

COPY /cloud_scripts /app

RUN chmod +x /app/update_miner-25.sh
RUN chmod +x /app/update_miner-1.sh
RUN chmod +x /app/update_miner-13.sh
RUN chmod +x /app/update_miner-20.sh
RUN chmod +x /app/update_miner-27.sh
RUN chmod +x /app/update_miner-4.sh
RUN chmod +x /app/update_miner-5.sh
RUN chmod +x /app/update_miner-16.sh
RUN chmod +x /app/update_miner-120.sh
RUN chmod +x /app/update_miner-15.sh
RUN chmod +x /app/update_miner-76.sh
RUN chmod +x /app/update_miner-61.sh
RUN chmod +x /app/update_miner-100.sh

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]