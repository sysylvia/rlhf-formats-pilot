const { Pool } = require('pg');

let pool = null;

function getDb() {
    if (!pool) {
        // Connection string from environment variable
        // Format: postgresql://username:password@host:port/database
        const connectionString = process.env.DATABASE_URL;
        
        if (!connectionString) {
            throw new Error('DATABASE_URL environment variable not set');
        }
        
        pool = new Pool({
            connectionString,
            ssl: process.env.NODE_ENV === 'production' ? {
                rejectUnauthorized: false
            } : false
        });
        
        // Test connection
        pool.query('SELECT NOW()', (err) => {
            if (err) {
                console.error('❌ Database connection failed:', err);
            } else {
                console.log('✅ Database connected successfully');
            }
        });
    }
    return pool;
}

async function closeDb() {
    if (pool) {
        await pool.end();
        pool = null;
    }
}

// Get current active experiment ID
async function getCurrentExperimentId() {
    const pool = getDb();
    const result = await pool.query(
        "SELECT id FROM experiments WHERE status = 'active' ORDER BY created_at DESC LIMIT 1"
    );
    
    if (result.rows.length === 0) {
        throw new Error('No active experiment found. Please create an experiment first.');
    }
    
    return result.rows[0].id;
}

module.exports = {
    getDb,
    closeDb,
    getCurrentExperimentId
};
