const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'purchase_order_db',
  password: process.env.DB_PASSWORD || 'password',
  port: process.env.DB_PORT || 5432,
});

// Initialize database schema
const initializeDatabase = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS purchase_orders (
        id SERIAL PRIMARY KEY,
        purchase_order_number VARCHAR(255) NOT NULL,
        image BYTEA,
        text TEXT,
        image_dimension VARCHAR(255),
        vehicle_number VARCHAR(255) NOT NULL,
        status VARCHAR(50) DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      
      CREATE INDEX IF NOT EXISTS idx_vehicle_number ON purchase_orders(vehicle_number);
      CREATE INDEX IF NOT EXISTS idx_purchase_order_number ON purchase_orders(purchase_order_number);
    `);
    console.log('Database schema initialized successfully');
  } catch (error) {
    console.error('Error initializing database:', error);
  }
};

// Test database connection
pool.on('connect', () => {
  console.log('Connected to PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

module.exports = { pool, initializeDatabase };
