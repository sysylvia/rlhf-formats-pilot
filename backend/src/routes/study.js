const express = require('express');
const router = express.Router();
const { getDb } = require('../models/db');

// Get study configuration
router.get('/config', (req, res) => {
    try {
        const db = getDb();
        const config = {};
        
        const rows = db.prepare('SELECT key, value FROM study_config').all();
        rows.forEach(row => {
            config[row.key] = row.value;
        });
        
        res.json({ config });
    } catch (error) {
        console.error('Error fetching config:', error);
        res.status(500).json({ error: 'Failed to fetch config' });
    }
});

// Update study configuration (admin)
router.post('/config', (req, res) => {
    try {
        const { key, value } = req.body;
        
        if (!key || value === undefined) {
            return res.status(400).json({ error: 'key and value required' });
        }
        
        const db = getDb();
        db.prepare(`
            INSERT INTO study_config (key, value, updated_at) 
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?
        `).run(key, value, new Date().toISOString(), value, new Date().toISOString());
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error updating config:', error);
        res.status(500).json({ error: 'Failed to update config' });
    }
});

// Get study statistics (admin)
router.get('/stats', (req, res) => {
    try {
        const db = getDb();
        
        const stats = {
            total_participants: db.prepare('SELECT COUNT(*) as cnt FROM participants').get().cnt,
            completed_participants: db.prepare('SELECT COUNT(*) as cnt FROM participants WHERE completed_at IS NOT NULL').get().cnt,
            total_annotations: db.prepare('SELECT COUNT(*) as cnt FROM annotations').get().cnt,
            annotations_by_format: {},
            prompts_count: db.prepare('SELECT COUNT(*) as cnt FROM prompts').get().cnt
        };
        
        const formatCounts = db.prepare('SELECT format, COUNT(*) as cnt FROM annotations GROUP BY format').all();
        formatCounts.forEach(row => {
            stats.annotations_by_format[row.format] = row.cnt;
        });
        
        res.json({ stats });
    } catch (error) {
        console.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

// Export data (admin)
router.get('/export/:table', (req, res) => {
    try {
        const { table } = req.params;
        const allowedTables = ['participants', 'annotations', 'prompts', 'task_assignments'];
        
        if (!allowedTables.includes(table)) {
            return res.status(400).json({ error: 'Invalid table name' });
        }
        
        const db = getDb();
        const data = db.prepare(`SELECT * FROM ${table}`).all();
        
        res.json({ 
            table,
            count: data.length,
            data 
        });
    } catch (error) {
        console.error('Error exporting data:', error);
        res.status(500).json({ error: 'Failed to export data' });
    }
});

module.exports = router;
