const express = require('express');
const router = express.Router();
const { getDb } = require('../models/db');

// Get all prompts (admin)
router.get('/', (req, res) => {
    try {
        const db = getDb();
        const prompts = db.prepare('SELECT * FROM prompts').all();
        res.json({ prompts });
    } catch (error) {
        console.error('Error fetching prompts:', error);
        res.status(500).json({ error: 'Failed to fetch prompts' });
    }
});

// Get single prompt
router.get('/:id', (req, res) => {
    try {
        const { id } = req.params;
        const db = getDb();
        const prompt = db.prepare('SELECT * FROM prompts WHERE id = ?').get(id);
        
        if (!prompt) {
            return res.status(404).json({ error: 'Prompt not found' });
        }
        
        res.json({ prompt });
    } catch (error) {
        console.error('Error fetching prompt:', error);
        res.status(500).json({ error: 'Failed to fetch prompt' });
    }
});

// Add prompt (admin)
router.post('/', (req, res) => {
    try {
        const { text, response_a, response_b, response_c, response_d, source, category } = req.body;
        
        if (!text || !response_a || !response_b) {
            return res.status(400).json({ error: 'text, response_a, and response_b are required' });
        }
        
        const db = getDb();
        const stmt = db.prepare(`
            INSERT INTO prompts (text, response_a, response_b, response_c, response_d, source, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `);
        
        const result = stmt.run(text, response_a, response_b, response_c || null, response_d || null, source || null, category || null);
        
        res.json({
            success: true,
            prompt_id: result.lastInsertRowid
        });
    } catch (error) {
        console.error('Error adding prompt:', error);
        res.status(500).json({ error: 'Failed to add prompt' });
    }
});

// Bulk add prompts (admin)
router.post('/bulk', (req, res) => {
    try {
        const { prompts } = req.body;
        
        if (!Array.isArray(prompts) || prompts.length === 0) {
            return res.status(400).json({ error: 'prompts array required' });
        }
        
        const db = getDb();
        const stmt = db.prepare(`
            INSERT INTO prompts (text, response_a, response_b, response_c, response_d, source, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `);
        
        const insertMany = db.transaction((prompts) => {
            for (const p of prompts) {
                stmt.run(p.text, p.response_a, p.response_b, p.response_c || null, p.response_d || null, p.source || null, p.category || null);
            }
        });
        
        insertMany(prompts);
        
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
