const express = require('express');
const router = express.Router();
const { getDb } = require('../models/db');

// Submit annotation
router.post('/', (req, res) => {
    try {
        const {
            participant_id,
            prompt_id,
            format,
            // Pairwise
            choice,
            confidence,
            // BWS
            best_choice,
            worst_choice,
            // Peer Prediction
            own_rating,
            predicted_avg,
            confidence_in_prediction,
            // Metadata
            duration_ms,
            order_shown,
            response_order
        } = req.body;
        
        if (!participant_id || !prompt_id || !format) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        const db = getDb();
        
        // Validate participant exists
        const participant = db.prepare('SELECT * FROM participants WHERE id = ?').get(participant_id);
        if (!participant) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        // Insert annotation
        const stmt = db.prepare(`
            INSERT INTO annotations (
                participant_id, prompt_id, format,
                choice, confidence,
                best_choice, worst_choice,
                own_rating, predicted_avg, confidence_in_prediction,
                duration_ms, order_shown, response_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        
        const result = stmt.run(
            participant_id, prompt_id, format,
            choice || null, confidence || null,
            best_choice || null, worst_choice || null,
            own_rating || null, predicted_avg || null, confidence_in_prediction || null,
            duration_ms || null, order_shown || null, response_order || null
        );
        
        // Mark task as completed (for within-subjects)
        if (participant.design_type === 'within') {
            db.prepare(`
                UPDATE task_assignments 
                SET completed = 1 
                WHERE participant_id = ? AND prompt_id = ? AND format = ?
            `).run(participant_id, prompt_id, format);
        }
        
        res.json({
            success: true,
            annotation_id: result.lastInsertRowid
        });
        
    } catch (error) {
        console.error('Error submitting annotation:', error);
        res.status(500).json({ error: 'Failed to submit annotation' });
    }
});

// Get next task for participant
router.get('/next/:participant_id', (req, res) => {
    try {
        const { participant_id } = req.params;
        const db = getDb();
        
        const participant = db.prepare('SELECT * FROM participants WHERE id = ?').get(participant_id);
        
        if (!participant) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        let nextTask;
        
        if (participant.design_type === 'within') {
            // Get next uncompleted task
            nextTask = db.prepare(`
                SELECT ta.*, p.text, p.response_a, p.response_b, p.response_c, p.response_d
                FROM task_assignments ta
                JOIN prompts p ON ta.prompt_id = p.id
                WHERE ta.participant_id = ? AND ta.completed = 0
                ORDER BY ta.assigned_at
                LIMIT 1
            `).get(participant_id);
        } else {
            // Between-subjects: get random uncompleted prompt for their assigned format
            const completedPrompts = db.prepare(`
                SELECT prompt_id FROM annotations WHERE participant_id = ?
            `).all(participant_id).map(r => r.prompt_id);
            
            const annotationsPerFormat = parseInt(db.prepare('SELECT value FROM study_config WHERE key = ?').get('annotations_per_format').value);
            
            if (completedPrompts.length >= annotationsPerFormat) {
                return res.json({ done: true });
            }
            
            const placeholders = completedPrompts.length > 0 ? completedPrompts.map(() => '?').join(',') : '';
            const query = completedPrompts.length > 0 
                ? `SELECT * FROM prompts WHERE id NOT IN (${placeholders}) ORDER BY RANDOM() LIMIT 1`
                : `SELECT * FROM prompts ORDER BY RANDOM() LIMIT 1`;
            
            const prompt = db.prepare(query).get(...completedPrompts);
            
            if (prompt) {
                nextTask = {
                    format: participant.format_assigned,
                    prompt_id: prompt.id,
                    text: prompt.text,
                    response_a: prompt.response_a,
                    response_b: prompt.response_b,
                    response_c: prompt.response_c,
                    response_d: prompt.response_d
                };
            }
        }
        
        if (!nextTask) {
            return res.json({ done: true });
        }
        
        res.json({
            done: false,
            task: {
                prompt_id: nextTask.prompt_id,
                format: nextTask.format,
                text: nextTask.text,
                responses: {
                    a: nextTask.response_a,
                    b: nextTask.response_b,
                    c: nextTask.response_c,
                    d: nextTask.response_d
                }
            }
        });
        
    } catch (error) {
        console.error('Error getting next task:', error);
        res.status(500).json({ error: 'Failed to get next task' });
    }
});

module.exports = router;
