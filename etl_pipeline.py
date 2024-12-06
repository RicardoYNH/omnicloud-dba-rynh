# etl_pipeline.py

import psycopg2
from pymongo import MongoClient
import docker
import os, datetime, subprocess, uuid, threading

def extract_postgres_data():
    # Conexion
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cursor = conn.cursor()
    
    # Extraer users
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return rows

def transform_data(rows):
    # Transformaciones de datos
    transformed_data = []
    for row in rows:
        transformed_data.append({
            'user_id': row[0],
            'name': row[1].upper(),  # Convertir el nombre a mayusculas
            'email': f"{row[2].split('@')[0]}@example.com",  # Cambiar el dominio del correo a example.com
            'unique_code': str(uuid.uuid4())  # Agregar un codigo unico por usuario
        })
    return transformed_data

def load_to_mongodb(data):
    # Conexion
    client = MongoClient(f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@{os.getenv('MONGO_HOST')}:27017/")
    db = client['db']
    users_collection = db['users_transformed']
    
    # Insertar a users_collection
    if data:
        users_collection.insert_many(data)
    
    client.close()

def etl_process():
    # Ejecutar ETL Pipeline
    extracted_data = extract_postgres_data()
    transformed_data = transform_data(extracted_data)
    load_to_mongodb(transformed_data)

def dump_postgres():
    # Crear dump de PostgreSQL
    TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"/backups/postgres_backup_{TIMESTAMP}.dump"
    print(f"Creando dump de PostgreSQL en {backup_file}...")

    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD")
        subprocess.run([
            "pg_dump",
            "-h", os.getenv("POSTGRES_HOST"),
            "-U", os.getenv("POSTGRES_USER"),
            "-d", os.getenv("POSTGRES_DB"),
            "-F", "c",
            "-f", backup_file
        ], env=env, check=True)
        print(f"Dump de PostgreSQL creado exitosamente: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error al crear el dump de PostgreSQL: {e}")

def dump_mongodb():
    # Crear dump de MongoDB en el contenedor de MongoDB y moverlo a /backups
    TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    archive_file = f"/mongo_backup_{TIMESTAMP}.dump"
    backup_file = f"/backups/mongo_backup_{TIMESTAMP}.dump"
    print(f"Creando dump de MongoDB en {archive_file}...")

    client = docker.from_env()

    try:
        # Ejecutar el dump de MongoDB dentro del contenedor de MongoDB usando Docker SDK
        mongodb_container = client.containers.get('mongodb')
        mongodb_container.exec_run(
            f"mongodump --username {os.getenv('MONGO_INITDB_ROOT_USERNAME')} "
            f"--password {os.getenv('MONGO_INITDB_ROOT_PASSWORD')} "
            f"--authenticationDatabase admin --db db --archive={archive_file}",
            user='root'
        )

        # Mover el archivo de dump al directorio de backups de la máquina anfitriona
        client.api.copy(mongodb_container.id, archive_file)
        with open(backup_file, 'wb') as f:
            for chunk in client.api.get_archive(mongodb_container.id, archive_file)[0]:
                f.write(chunk)

        # Eliminar el archivo de dump del contenedor para liberar espacio
        mongodb_container.exec_run(f"rm {archive_file}")

        print(f"Dump de MongoDB creado y movido exitosamente: {backup_file}")
    except docker.errors.DockerException as e:
        print(f"Error al crear el dump de MongoDB: {e}")

def target():
    dump_mongodb()

if __name__ == '__main__':
    # Primero respaldos, despues procesamiento
    dump_postgres()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=10)
    etl_process()
