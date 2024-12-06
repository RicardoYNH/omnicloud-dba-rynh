#!/bin/sh
# backup_script.sh

# directorio backups
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR
chmod -R 777 $BACKUP_DIR

# Esperar a que PostgreSQL y MongoDB estén listos
echo "Esperando a que PostgreSQL esté listo..."
until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  sleep 2
done

echo "Esperando a que MongoDB esté listo..."
until nc -z $MONGO_HOST 27017; do
  sleep 2
done

# Ejecutar ETL Pipeline
run_etl_pipeline() {
  echo "Ejecutando ETL Pipeline (Backups)..."
  python /etl_pipeline.py
  echo "Proceso ETL completado."
}

# Ejecutar respaldos de PostgreSQL y MongoDB
run_etl_pipeline
