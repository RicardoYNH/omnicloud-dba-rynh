# Dockerfile

# Imagen Python
FROM python:3.9-buster

# Sistema y herramientas
RUN apt-get update && \
    apt-get install -y docker-ce-cli postgresql-client mongo-tools mongodb-org-shell cron netcat curl wget gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify Docker CLI installation
RUN docker --version

# Librerías Python
RUN pip install --no-cache-dir docker psycopg2-binary pymongo kafka-python elasticsearch

# Entorno
#ENV PATH="/usr/bin:"

ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=db
ENV POSTGRES_HOST=postgres_db
ENV POSTGRES_PORT=5432

ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=password
ENV MONGO_HOST=mongodb

# Copiar scripts a container
COPY etl_pipeline.py /etl_pipeline.py
COPY kafka_consumer.py /kafka_consumer.py
COPY kafka_producer.py /kafka_producer.py
COPY backup_script.sh /backup_script.sh
RUN chmod +x /backup_script.sh

# Crontab (cada hora)
RUN (echo "0 * * * * /bin/sh /backup_script.sh" >> /etc/cron.d/backup_cron)

# Punto de entrada: Primera ejecución y luego cron en foreground
ENTRYPOINT ["/bin/sh", "-c", "/backup_script.sh && cron -f"]
