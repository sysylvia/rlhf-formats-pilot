const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const SCHEMA_PATH = path.join(__dirname, '../models/schema-postgres.sql');

async function initializeDatabase() {
    console.log('Initializing PostgreSQL database...');
    
    const connectionString = process.env.DATABASE_URL;
    
    if (!connectionString) {
        throw new Error('DATABASE_URL environment variable not set');
    }
    
    const pool = new Pool({
        connectionString,
        ssl: process.env.NODE_ENV === 'production' ? {
            rejectUnauthorized: false
        } : false
    });
    
    try {
        // Read and execute schema
        const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');
        await pool.query(schema);
        
        console.log('✅ Database initialized successfully');
        console.log(`📁 Connection: ${connectionString.split('@')[1]}`); // Hide credentials
    } catch (error) {
        console.error('❌ Database initialization failed:', error);
        throw error;
    } finally {
        await pool.end();
    }
}

// Run if called directly
if (require.main === module) {
    initializeDatabase()
        .then(() => process.exit(0))
        .catch((error) => {
            console.error(error);
            process.exit(1);
        });
}

module.exports = { initializeDatabase };
