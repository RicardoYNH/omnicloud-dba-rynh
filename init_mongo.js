// init_mongo.js

// Conectar a la base de datos y crear las colecciones 'logs' y 'users_transformed' con algunos registros aleatorios

const db = connect('mongodb://admin:password@localhost:27017/admin');

// Seleccionar la base de datos (creará la base de datos si no existe)
db = db.getSiblingDB('db');

// Crear la colección 'logs' y añadir registros aleatorios
db.createCollection('logs');

db.logs.insertMany([
  { user_id: 1, timestamp: new Date(), level: 'INFO', message: 'Sistema inicializado ' },
  { user_id: 3, timestamp: new Date(), level: 'WARN', message: 'Memoria baja' },
  { user_id: 4, timestamp: new Date(), level: 'ERROR', message: 'Fallo' },
  { user_id: 4, timestamp: new Date(), level: 'INFO', message: 'Conexión' },
  { user_id: 5, timestamp: new Date(), level: 'DEBUG', message: 'Debugging activado' }
]);

// Crear la colección 'users_transformed'
db.createCollection('users_transformed');
