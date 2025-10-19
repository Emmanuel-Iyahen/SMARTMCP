FROM apache/airflow:2.9.2-python3.10

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /opt/airflow/entrypoint.sh
