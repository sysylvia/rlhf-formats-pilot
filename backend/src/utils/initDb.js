const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, '../../data/pilot.db');
const SCHEMA_PATH = path.join(__dirname, '../models/schema.sql');

function initializeDatabase() {
    console.log('Initializing database...');
    
    // Create data directory if it doesn't exist
    const dataDir = path.dirname(DB_PATH);
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }
    
    // Create/open database
    const db = new Database(DB_PATH);
    
    // Read and execute schema
    const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');
    db.exec(schema);
    
    console.log('✅ Database initialized successfully');
    console.log(`📁 Location: ${DB_PATH}`);
    
    db.close();
}

// Run if called directly
if (require.main === module) {
    initializeDatabase();
}

module.exports = { initializeDatabase };
