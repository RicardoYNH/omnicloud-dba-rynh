  

# OMNICLOUD Prueba técnica v2

**Prueba Técnica: Docker, ETL y Big Data**

**Perfil: DBA Mid**

 **Ricardo Yair Nava Hernández**

La presente documentación detalla el entorno de datos implementado y su manejo, aplicando principios de Docker, Postgre SQL, Mongo DB, ETL Pipelines, Big Data, Python, Linux, Kafka, ElasticSearch, Zookeeper y Kibana; a través de cuatro secciones principales:

1. Instrucciones para ejecutar el entorno.
2. Detalles sobre cómo realizar la normalización.
3. Descripción del proceso ETL.
4. Uso de Kafka Y Elasticsearch.

A continuación, los componentes y contenedores implementados:

- **Docker**: Plataforma de entorno contenido para la aplicación.
  - **docker-compose.yml**: Archivo de configuración YAML para la aplicación y entorno de contenedores.
   - **Dockerfile**: Archivo de configuración adicional para el entorno del contenedor de administración de flujo de datos.
-  **PostgreSQL**: Base de datos normalizada a 3FN. Origen de la ETL Pipeline. 
   - **init_postgres.sql**: Inicializar base de datos SQL.
   - **queries.sql**: Consultas simples en SQL.
-  **MongoDB**: Base de datos NoSQL. Destino de la ETL Pipeline.
   - **init_mongo.js**: Inicializar base de datos MongoDB.
-  **Python**: Lenguaje utilizado en scripts para ETL Pipeline, database dumps y comunicación entre procesos Big Data.
   - **etl_pipeline.py**: Proceso de flujo de datos que realiza respaldos periódicos de las bases de datos y un proceso de comunicación entre ambas.
   - **kafka_producer.py**: Productor de nuestro proceso adicional de Big Data basado en Apache Kafka.
   - **kafka_consumer.py**: Receptor de nuestro proceso adicional de Big Data basado en ElasticSearch.
-  **Apache Kafka**: Contenedor distribuido de transmisión para Big Data.
-  **Elasticsearch**: Contenedor distribuido de recepción, búsqueda y análisis para Big Data.
- **Zookeeper**: Contenedor del servicio centralizado de comunicación entre Kafka y ElasticSearch
- **Kibana**: Herramienta inicializada y lista para comenzar el desarrollo de visualizaciones.
- **Bash**: Comandos de consola y script .sh para administrar ETL Pipeline.
    - **backup_script.sh**: Script para crear el directorio de backups y esperar a que las bases de datos estén en línea antes de comenzar la programación de la ETL Pipeline.

El objetivo principal es crear un entorno de Big Data demostrativo basado en contenedores Docker.   

# 1. Instrucciones para Ejecutar el Entorno

Es necesario contar con **Docker** y **Docker Compose** instalado.  [Docker Official](https://www.docker.com/get-started). Puede clonarse el repositorio mediante **Github**, o descargando manualmente.

### 1.  **Clonar el Repositorio**
```sh
git  clone  https://github.com/RicardoYNH/omnicloud-dba-rynh.git
cd  omnicloud-dba-rynh
```
### 2.  **Desplegar en Docker**

En el terminal de docker, navegar al directorio del repositorio, y desplegar en entorno con:
```sh
docker-compose build --no-cache
docker-compose up -d
```
Esto levantará todos los contenedores en la interfaz de Docker, pudiendo validar que todos los servicios estén activos.

### 3.  **Acceso a Servicios**

-  **PostgreSQL**: Está disponible en el puerto `5432`. Permitiendo conexión mediante cualquier cliente SQL como `psql` o herramientas como DBeaver, utilizando las credenciales proporcionadas en `docker-compose.yml`. url:`postgresql://user:password@postgres_db:5432/db`.
-  **MongoDB**: Está disponible en el puerto `27017`. Permitiendo conexión mediante herramientas como MongoDB Compass para explorar la base de datos. url:`mongodb://admin:password@mongodb:27017/db?authSource=admin`
- **Kafka, ElasticSearch y Zookeeper**: Respectivamente en los puertos `9092, (9200, 9300), 2181`.
-  **Kibana**: Para visualizar los datos indexados en Elasticsearch, abrir `http://localhost:5601` en el navegador.

### 4.  **Ejecución de Servicios**

- **ETL Pipeline:**

El pipeline de ETL se activa automáticamente al inicializar el entorno, automatizando el respaldo de base de datos y la comunicación de información sobre usuarios transformada. 
Además, queda programada para ejecución cada hora mediante `cron`.

- **Consultas SQL:**

Las consultas definidas en `queries.sql` pueden ejecutarse dentro del contenedor de PostgreSQL con el siguiente comando:
```sh
docker  exec  -it  postgres_db  psql  -U  user  -d  db  -f  /queries.sql
```
- **BigData: Kafka Producer y ElasticSearch Consumer:**

Para enviar eventos al tópico `user_events` usando el productor Kafka:
```sh
docker  exec  -it  etl_pipeline  python  /kafka_producer.py
```
Para ejecutar el consumidor Kafka y enviar datos a Elasticsearch:
```sh
docker  exec  -it  etl_pipeline  python  /kafka_consumer.py
```

### 5.  **Detener Entorno**
- Para detener todos los servicios, desde la terminal de docker ejecuta:
```sh
docker-compose  down -v
```
Los volúmenes de datos permanecerán para mantener la persistencia de los datos. Sin embargo, el atributo `--no-cache` en la inicialización los elimina, así que puede opcionalmente omitirse.

# 2. Detalles sobre la Normalización
Se normalizó la base de datos SQL original hasta alcanzar la **Tercera Forma Normal (3FN)**, garantizando una estructura eficiente y optimizada para las consultas.

### Base de Datos Original
La base de datos original constaba de una única tabla llamada `orders`, que contenía los siguientes campos:
  ```sql
CREATE  TABLE  orders (
order_id SERIAL,
customer_name TEXT,
product_name TEXT,
product_price NUMERIC,
order_date TIMESTAMP
);
```
Algunos problemas relacionados con esta disposición son:
-  **Redundancia**: Cada vez que se realiza un pedido, la información del cliente (`customer_name`) y del producto (`product_name` y `product_price`) se repite, lo cual genera redundancia y aumenta el espacio utilizado en la base de datos.
-  **Dificultad para Actualizar**: Si, por ejemplo, el precio de un producto cambia, es necesario actualizar cada fila que contenga ese producto, lo cual es propenso a errores.

### Proceso de Normalización

Para optimizar la estructura de la base de datos, realizamos el proceso de normalización dividiendo la tabla `orders` en tres tablas independientes: `users`, `products` y `orders`, asegurando que cada tabla contenga solo datos específicos y eliminando la redundancia, además, se implementa el uso de llaves e índices.

**Estructura de las Tablas Normalizadas:**

1.  **Tabla `users`**: Esta tabla almacena información única de cada usuario.
```sql
CREATE  TABLE  users (
user_id SERIAL  PRIMARY KEY,
name  TEXT  UNIQUE,
email TEXT
);
```
2.  **Tabla `products`**: Esta tabla almacena información única de cada producto.
```sql
CREATE  TABLE  products (
product_id SERIAL  PRIMARY KEY,
product_name TEXT  UNIQUE,
product_price NUMERIC
);
```
3.  **Tabla `orders`**: Esta tabla almacena los pedidos, referenciando a los usuarios y productos mediante claves externas.
```sql
CREATE  TABLE  orders (
order_id SERIAL  PRIMARY KEY,
user_id INT  REFERENCES users(user_id),
product_id INT  REFERENCES products(product_id),
order_date TIMESTAMP
);
```
Cada base ahora cuenta con un `KEY` serializado para eficientar las operaciones, y además se agregan índices en campos de especial relevancia:
```sql
CREATE  INDEX  idx_user_name  ON users (name);
CREATE  INDEX  idx_product_name  ON products (product_name);
CREATE  INDEX  idx_order_date  ON orders (order_date);
CREATE  INDEX  idx_user_email  ON users (email);
```
# 3. Descripción del Proceso ETL

El proceso ETL se lleva a cabo mediante el script `etl_process.py`, que automatiza la transferencia de datos desde PostgreSQL hacia MongoDB, transformando los datos en el proceso. Tres funciones toman la forma de cada fase en este proceso:

1. **Extracción:** `extract_postgres_data() ` establece la conexión con la base Postgres y guarda el resultado de la consulta `SELECT * FROM users`.
2. **Transformación:** `transform_data() `realiza las tres transformaciones solicitadas (nombre de usuario a mayúsculas, dominio de correo a @example.com y agregar un código único por usuario) a la información obtenida en el paso anterior.
3. **Carga:** `load_to_mongodb() ` establece la conexión con la base MongoDB y ejecuta un `inser_many()` en la colección `users_transformed` de toda la información obtenida en el paso anterior.

# 4. Uso de Kafka y Elasticsearch

Se ha implementado el uso de **Apache Kafka** y **Elasticsearch** para manejar y analizar los eventos generados en tiempo real. La integración de estos servicios permite recibir, procesar, indexar, y visualizar datos de eventos en tiempo real, utilizando un sistema desacoplado y escalable. 

### Contenedores Involucrados:

1. **ZooKeeper:** Servicio centralizado utilizado para la coordinación y gestión de la configuración del clúster de Kafka. Apache Kafka depende de ZooKeeper para coordinar la información del clúster, como qué brokers están disponibles y cuál es el líder para cada partición de un tópico.
En el archivo `docker-compose.yml`, ZooKeeper se configura de la siguiente manera:
```yaml
zookeeper:
	image:  bitnami/zookeeper:latest
	container_name:  zookeeper
	ports:
		-  "2181:2181"
	environment:
		-  ALLOW_ANONYMOUS_LOGIN=yes
```
Cabe destacar que, para fines demostrativos del ejercicio, se omite autenticación mediante `ALLOW_ANONYMOUS_LOGIN=yes`.

2. **Kafka:** Plataforma distribuida de transmisión de datos en tiempo real. Se utiliza para recibir eventos generados por usuarios y ponerlos a disposición de otros servicios de manera eficiente.
El contenedor de Kafka se configura de la siguiente manera en `docker-compose.yml`:
```yaml
kafka:
	image:  bitnami/kafka:latest
	container_name:  kafka
	ports:
		-  "9092:9092"
	environment:
		KAFKA_ZOOKEEPER_CONNECT:  zookeeper:2181
		KAFKA_ADVERTISED_LISTENERS:  PLAINTEXT://kafka:9092
		KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR:  1
	volumes:
		-  /var/run/docker.sock:/var/run/docker.sock
	depends_on:
		-  zookeeper
```
Kafka depende de ZooKeeper, por lo que utilizamos `depends_on` para asegurar que ZooKeeper esté listo antes de iniciar.

3. **Elasticsearch:** Motor de búsqueda y análisis que se utiliza para indexar y almacenar datos de eventos en tiempo real. Recibe los datos consumidos de Kafka y los hace accesibles para la visualización y análisis en Kibana.
El contenedor de Elasticsearch se configura de la siguiente manera:
```yaml
elasticsearch:
	image:  docker.elastic.co/elasticsearch/elasticsearch:7.9.2
	container_name:  elasticsearch
	environment:
		-  discovery.type=single-node
		-  ES_JAVA_OPTS=-Xms512m -Xmx512m
	volumes:
		-  elastic_data:/usr/share/elasticsearch/data
	ports:
		-  "9200:9200"
		-  "9300:9300"
```
El puerto `9200` se utiliza para la API REST de Elasticsearch, y el puerto `9300` para la comunicación interna entre nodos.

4. **Kibana:** Herramienta de visualización que permite analizar y explorar los datos almacenados en Elasticsearch. Se conecta a Elasticsearch para proporcionar una interfaz gráfica que está lista para desarrollar visualizaciones de los eventos producidos en Kafka.
El contenedor de Kibana se configura de la siguiente manera:
```yaml
kibana:
	image:  docker.elastic.co/kibana/kibana:7.9.2
	container_name:  kibana
	ports:
		-  "5601:5601"
	environment:
		ELASTICSEARCH_URL:  http://elasticsearch:9200
	depends_on:
		-  elasticsearch
```
Kibana depende de Elasticsearch, por lo que utilizamos `depends_on` para asegurar que Elasticsearch esté listo antes de iniciar.

### Scripts de Python y Su Interacción

1. **Productor Kafka (`kafka_producer.py`)**

El script `kafka_producer.py` utiliza `kafka-python` para generar eventos y enviarlos al tópico `user_events` en Kafka. Estos eventos representan acciones o registros generados por los usuarios, que luego serán consumidos y almacenados para su análisis.

Puede ejecutarse manualmente desde el container `etl_pipeline` con:
```sh
python  /kafka_producer.py
```
O directamente desde la consola de Docker con:
```sh
docker  exec  -it  etl_pipeline  python  /kafka_producer.py
```

2. **Consumidor Kafka (`kafka_consumer.py`)**

El script `kafka_consumer.py` actúa como un consumidor que escucha el tópico `user_events` en Kafka y, cada vez que se recibe un evento, lo procesa y lo envía a Elasticsearch para ser indexado.  

Se utiliza `KafkaConsumer` de `kafka-python` para conectarse al tópico `user_events`. La librería `elasticsearch` se conecta a  Elasticsearch y envía los datos que se reciben del consumidor Kafka. Cada evento recibido se indexa en Elasticsearch en el índice `user_events`.

Puede ejecutarse manualmente desde el container `etl_pipeline` con:
```sh
python  /kafka_consumer.py
```
O directamente desde la consola de Docker con:
```sh
docker  exec  -it  etl_pipeline  python  /kafka_consumer.py
```


3.  **Visualización de Datos (Kibana)**

Se puede acceder a Kibana desde el navegador en `http://localhost:5601` para comenzar el desarrollo de dashboards y gráficos que analicen los eventos en tiempo real y generen reportes de utilidad.
