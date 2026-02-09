const express = require('express');
const router = express.Router();
const { getDb, getCurrentExperimentId } = require('../models/db');

// Get study configuration
router.get('/config', async (req, res) => {
    try {
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        const config = {};
        
        const result = await pool.query(
            'SELECT key, value FROM study_config WHERE experiment_id = $1',
            [experimentId]
        );
        
        result.rows.forEach(row => {
            config[row.key] = row.value;
        });
        
        res.json({ config });
    } catch (error) {
        console.error('Error fetching config:', error);
        res.status(500).json({ error: 'Failed to fetch config' });
    }
});

// Update study configuration (admin)
router.post('/config', async (req, res) => {
    try {
        const { key, value } = req.body;
        
        if (!key || value === undefined) {
            return res.status(400).json({ error: 'key and value required' });
        }
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        await pool.query(`
            INSERT INTO study_config (experiment_id, key, value, updated_at) 
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (experiment_id, key) 
            DO UPDATE SET value = $3, updated_at = NOW()
        `, [experimentId, key, value]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error updating config:', error);
        res.status(500).json({ error: 'Failed to update config' });
    }
});

// Get study statistics (admin)
router.get('/stats', async (req, res) => {
    try {
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const totalParticipantsResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM participants WHERE experiment_id = $1',
            [experimentId]
        );
        
        const completedParticipantsResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM participants WHERE experiment_id = $1 AND completed_at IS NOT NULL',
            [experimentId]
        );
        
        const totalAnnotationsResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM annotations WHERE experiment_id = $1',
            [experimentId]
        );
        
        const formatCountsResult = await pool.query(
            'SELECT format, COUNT(*) as cnt FROM annotations WHERE experiment_id = $1 GROUP BY format',
            [experimentId]
        );
        
        const promptsCountResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM prompts WHERE experiment_id = $1 OR experiment_id IS NULL',
            [experimentId]
        );
        
        const stats = {
            total_participants: parseInt(totalParticipantsResult.rows[0].cnt),
            completed_participants: parseInt(completedParticipantsResult.rows[0].cnt),
            total_annotations: parseInt(totalAnnotationsResult.rows[0].cnt),
            annotations_by_format: {},
            prompts_count: parseInt(promptsCountResult.rows[0].cnt)
        };
        
        formatCountsResult.rows.forEach(row => {
            stats.annotations_by_format[row.format] = parseInt(row.cnt);
        });
        
        res.json({ stats });
    } catch (error) {
        console.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

// Export data (admin)
router.get('/export/:table', async (req, res) => {
    try {
        const { table } = req.params;
        const allowedTables = ['participants', 'annotations', 'prompts', 'task_assignments'];
        
        if (!allowedTables.includes(table)) {
            return res.status(400).json({ error: 'Invalid table name' });
        }
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const result = await pool.query(
            `SELECT * FROM ${table} WHERE experiment_id = $1`,
            [experimentId]
        );
        
        res.json({ 
            table,
            experiment_id: experimentId,
            count: result.rows.length,
            data: result.rows
        });
    } catch (error) {
        console.error('Error exporting data:', error);
        res.status(500).json({ error: 'Failed to export data' });
    }
});

module.exports = router;
