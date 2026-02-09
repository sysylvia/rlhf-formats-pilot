const express = require('express');
const router = express.Router();
const { getDb, getCurrentExperimentId } = require('../models/db');

// Get all prompts (admin)
router.get('/', async (req, res) => {
    try {
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const result = await pool.query(
            'SELECT * FROM prompts WHERE experiment_id = $1 OR experiment_id IS NULL',
            [experimentId]
        );
        
        res.json({ prompts: result.rows });
    } catch (error) {
        console.error('Error fetching prompts:', error);
        res.status(500).json({ error: 'Failed to fetch prompts' });
    }
});

// Get single prompt
router.get('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const pool = getDb();
        
        const result = await pool.query('SELECT * FROM prompts WHERE id = $1', [id]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Prompt not found' });
        }
        
        res.json({ prompt: result.rows[0] });
    } catch (error) {
        console.error('Error fetching prompt:', error);
        res.status(500).json({ error: 'Failed to fetch prompt' });
    }
});

// Add prompt (admin)
router.post('/', async (req, res) => {
    try {
        const { text, response_a, response_b, response_c, response_d, source, category } = req.body;
        
        if (!text || !response_a || !response_b) {
            return res.status(400).json({ error: 'text, response_a, and response_b are required' });
        }
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const result = await pool.query(`
            INSERT INTO prompts (experiment_id, text, response_a, response_b, response_c, response_d, source, category)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        `, [experimentId, text, response_a, response_b, response_c, response_d, source, category]);
        
        res.json({
            success: true,
            prompt_id: result.rows[0].id
        });
    } catch (error) {
        console.error('Error adding prompt:', error);
        res.status(500).json({ error: 'Failed to add prompt' });
    }
});

// Bulk add prompts (admin)
router.post('/bulk', async (req, res) => {
    try {
        const { prompts } = req.body;
        
        if (!Array.isArray(prompts) || prompts.length === 0) {
            return res.status(400).json({ error: 'prompts array required' });
        }
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const client = await pool.connect();
        
        try {
            await client.query('BEGIN');
            
            for (const p of prompts) {
                await client.query(`
                    INSERT INTO prompts (experiment_id, text, response_a, response_b, response_c, response_d, source, category)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                `, [experimentId, p.text, p.response_a, p.response_b, p.response_c || null, p.response_d || null, p.source || null, p.category || null]);
            }
            
            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
        
        res.json({
            success: true,
            inserted: prompts.length
        });
    } catch (error) {
        console.error('Error bulk adding prompts:', error);
        res.status(500).json({ error: 'Failed to bulk add prompts' });
    }
});

module.exports = router;
