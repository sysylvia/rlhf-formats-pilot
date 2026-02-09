const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const { getDb, getCurrentExperimentId } = require('../models/db');

// Register new participant (from Prolific)
router.post('/register', async (req, res) => {
    try {
        const { prolific_pid } = req.body;
        
        if (!prolific_pid) {
            return res.status(400).json({ error: 'prolific_pid required' });
        }
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        // Check if already registered
        const existingResult = await pool.query(
            'SELECT * FROM participants WHERE prolific_pid = $1 AND experiment_id = $2',
            [prolific_pid, experimentId]
        );
        
        if (existingResult.rows.length > 0) {
            const existing = existingResult.rows[0];
            return res.json({ 
                participant_id: existing.id,
                completion_code: existing.completion_code,
                format_assigned: existing.format_assigned,
                design_type: existing.design_type,
                already_registered: true
            });
        }
        
        // Get study config
        const configResult = await pool.query(
            'SELECT key, value FROM study_config WHERE experiment_id = $1',
            [experimentId]
        );
        const config = {};
        configResult.rows.forEach(row => {
            config[row.key] = row.value;
        });
        
        const designType = config.design_type || 'within';
        const formatsEnabled = (config.formats_enabled || 'pairwise,bws,peer_prediction').split(',');
        
        // Assign format
        let formatAssigned;
        if (designType === 'within') {
            formatAssigned = 'all'; // Will do all formats
        } else {
            // Between-subjects: balance assignment
            const counts = {};
            for (const format of formatsEnabled) {
                const countResult = await pool.query(
                    'SELECT COUNT(*) as cnt FROM participants WHERE format_assigned = $1 AND experiment_id = $2',
                    [format, experimentId]
                );
                counts[format] = parseInt(countResult.rows[0].cnt);
            }
            // Assign to format with fewest participants
            formatAssigned = Object.entries(counts).sort((a, b) => a[1] - b[1])[0][0];
        }
        
        // Generate completion code
        const completionCode = `RLHF2026-${uuidv4().split('-')[0].toUpperCase()}`;
        
        // Insert participant
        const insertResult = await pool.query(
            `INSERT INTO participants (experiment_id, prolific_pid, format_assigned, design_type, completion_code, started_at)
             VALUES ($1, $2, $3, $4, $5, NOW())
             RETURNING id`,
            [experimentId, prolific_pid, formatAssigned, designType, completionCode]
        );
        
        const participantId = insertResult.rows[0].id;
        
        // For within-subjects, create task assignments
        if (designType === 'within') {
            const annotationsPerFormat = parseInt(config.annotations_per_format || '15');
            
            // Get random prompts for each format
            const promptsResult = await pool.query(
                'SELECT id FROM prompts WHERE experiment_id = $1 OR experiment_id IS NULL ORDER BY RANDOM() LIMIT $2',
                [experimentId, annotationsPerFormat * formatsEnabled.length]
            );
            
            const allPrompts = promptsResult.rows;
            
            let idx = 0;
            for (const format of formatsEnabled) {
                for (let i = 0; i < annotationsPerFormat; i++) {
                    await pool.query(
                        'INSERT INTO task_assignments (experiment_id, participant_id, prompt_id, format) VALUES ($1, $2, $3, $4)',
                        [experimentId, participantId, allPrompts[idx].id, format]
                    );
                    idx++;
                }
            }
        }
        
        res.json({
            participant_id: participantId,
            completion_code: completionCode,
            format_assigned: formatAssigned,
            design_type: designType
        });
        
    } catch (error) {
        console.error('Error registering participant:', error);
        res.status(500).json({ error: 'Failed to register participant' });
    }
});

// Record consent
router.post('/:id/consent', async (req, res) => {
    try {
        const { id } = req.params;
        const pool = getDb();
        
        await pool.query('UPDATE participants SET consent_given = TRUE WHERE id = $1', [id]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error recording consent:', error);
        res.status(500).json({ error: 'Failed to record consent' });
    }
});

// Record instructions completed
router.post('/:id/instructions', async (req, res) => {
    try {
        const { id } = req.params;
        const pool = getDb();
        
        await pool.query('UPDATE participants SET instructions_completed = TRUE WHERE id = $1', [id]);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error recording instructions:', error);
        res.status(500).json({ error: 'Failed to record instructions' });
    }
});

// Mark participant as completed
router.post('/:id/complete', async (req, res) => {
    try {
        const { id } = req.params;
        const pool = getDb();
        
        const participantResult = await pool.query(
            'SELECT completion_code FROM participants WHERE id = $1',
            [id]
        );
        
        if (participantResult.rows.length === 0) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        const participant = participantResult.rows[0];
        
        await pool.query('UPDATE participants SET completed_at = NOW() WHERE id = $1', [id]);
        
        res.json({ 
            success: true,
            completion_code: participant.completion_code 
        });
    } catch (error) {
        console.error('Error completing participant:', error);
        res.status(500).json({ error: 'Failed to mark as complete' });
    }
});

// Get participant progress
router.get('/:id/progress', async (req, res) => {
    try {
        const { id } = req.params;
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        const participantResult = await pool.query(
            'SELECT * FROM participants WHERE id = $1',
            [id]
        );
        
        if (participantResult.rows.length === 0) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        const participant = participantResult.rows[0];
        
        // Get completion stats
        const completedResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM annotations WHERE participant_id = $1',
            [id]
        );
        const completed = parseInt(completedResult.rows[0].cnt);
        
        let total;
        if (participant.design_type === 'within') {
            const totalResult = await pool.query(
                'SELECT COUNT(*) as cnt FROM task_assignments WHERE participant_id = $1',
                [id]
            );
            total = parseInt(totalResult.rows[0].cnt);
        } else {
            const configResult = await pool.query(
                'SELECT value FROM study_config WHERE experiment_id = $1 AND key = $2',
                [experimentId, 'annotations_per_format']
            );
            const annotationsPerFormat = parseInt(configResult.rows[0]?.value || '15');
            total = annotationsPerFormat;
        }
        
        res.json({
            participant_id: participant.id,
            design_type: participant.design_type,
            format_assigned: participant.format_assigned,
            completed: completed,
            total: total,
            progress_percent: Math.round((completed / total) * 100)
        });
        
    } catch (error) {
        console.error('Error getting progress:', error);
        res.status(500).json({ error: 'Failed to get progress' });
    }
});

module.exports = router;
