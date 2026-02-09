const express = require('express');
const router = express.Router();
const { getDb, getCurrentExperimentId } = require('../models/db');

// Submit annotation
router.post('/', async (req, res) => {
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
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        // Validate participant exists
        const participantResult = await pool.query(
            'SELECT * FROM participants WHERE id = $1',
            [participant_id]
        );
        
        if (participantResult.rows.length === 0) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        const participant = participantResult.rows[0];
        
        // Insert annotation
        const result = await pool.query(`
            INSERT INTO annotations (
                experiment_id, participant_id, prompt_id, format,
                choice, confidence,
                best_choice, worst_choice,
                own_rating, predicted_avg, confidence_in_prediction,
                duration_ms, order_shown, response_order
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id
        `, [
            experimentId, participant_id, prompt_id, format,
            choice, confidence,
            best_choice, worst_choice,
            own_rating, predicted_avg, confidence_in_prediction,
            duration_ms, order_shown, response_order
        ]);
        
        // Mark task as completed (for within-subjects)
        if (participant.design_type === 'within') {
            await pool.query(`
                UPDATE task_assignments 
                SET completed = TRUE 
                WHERE participant_id = $1 AND prompt_id = $2 AND format = $3
            `, [participant_id, prompt_id, format]);
        }
        
        res.json({
            success: true,
            annotation_id: result.rows[0].id
        });
        
    } catch (error) {
        console.error('Error submitting annotation:', error);
        res.status(500).json({ error: 'Failed to submit annotation' });
    }
});

// Get next task for participant
router.get('/next/:participant_id', async (req, res) => {
    try {
        const { participant_id } = req.params;
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const participantResult = await pool.query(
            'SELECT * FROM participants WHERE id = $1',
            [participant_id]
        );
        
        if (participantResult.rows.length === 0) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        const participant = participantResult.rows[0];
        let nextTask;
        
        if (participant.design_type === 'within') {
            // Get next uncompleted task
            const taskResult = await pool.query(`
                SELECT ta.*, p.text, p.response_a, p.response_b, p.response_c, p.response_d
                FROM task_assignments ta
                JOIN prompts p ON ta.prompt_id = p.id
                WHERE ta.participant_id = $1 AND ta.completed = FALSE
                ORDER BY ta.assigned_at
                LIMIT 1
            `, [participant_id]);
            
            nextTask = taskResult.rows[0];
        } else {
            // Between-subjects: get random uncompleted prompt for their assigned format
            const completedPromptsResult = await pool.query(
                'SELECT prompt_id FROM annotations WHERE participant_id = $1',
                [participant_id]
            );
            
            const completedPrompts = completedPromptsResult.rows.map(r => r.prompt_id);
            
            const configResult = await pool.query(
                'SELECT value FROM study_config WHERE experiment_id = $1 AND key = $2',
                [experimentId, 'annotations_per_format']
            );
            
            const annotationsPerFormat = parseInt(configResult.rows[0]?.value || '15');
            
            if (completedPrompts.length >= annotationsPerFormat) {
                return res.json({ done: true });
            }
            
            let promptResult;
            if (completedPrompts.length > 0) {
                promptResult = await pool.query(
                    'SELECT * FROM prompts WHERE (experiment_id = $1 OR experiment_id IS NULL) AND id != ALL($2) ORDER BY RANDOM() LIMIT 1',
                    [experimentId, completedPrompts]
                );
            } else {
                promptResult = await pool.query(
                    'SELECT * FROM prompts WHERE experiment_id = $1 OR experiment_id IS NULL ORDER BY RANDOM() LIMIT 1',
                    [experimentId]
                );
            }
            
            const prompt = promptResult.rows[0];
            
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
