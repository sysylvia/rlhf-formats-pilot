const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const { getDb } = require('../models/db');

// Register new participant (from Prolific)
router.post('/register', (req, res) => {
    try {
        const { prolific_pid } = req.body;
        
        if (!prolific_pid) {
            return res.status(400).json({ error: 'prolific_pid required' });
        }
        
        const db = getDb();
        
        // Check if already registered
        const existing = db.prepare('SELECT * FROM participants WHERE prolific_pid = ?').get(prolific_pid);
        if (existing) {
            return res.json({ 
                participant_id: existing.id,
                completion_code: existing.completion_code,
                format_assigned: existing.format_assigned,
                design_type: existing.design_type,
                already_registered: true
            });
        }
        
        // Get study config
        const designType = db.prepare('SELECT value FROM study_config WHERE key = ?').get('design_type').value;
        const formatsEnabled = db.prepare('SELECT value FROM study_config WHERE key = ?').get('formats_enabled').value.split(',');
        
        // Assign format
        let formatAssigned;
        if (designType === 'within') {
            formatAssigned = 'all'; // Will do all formats
        } else {
            // Between-subjects: balance assignment
            const counts = {};
            formatsEnabled.forEach(f => {
                const count = db.prepare('SELECT COUNT(*) as cnt FROM participants WHERE format_assigned = ?').get(f).cnt;
                counts[f] = count;
            });
            // Assign to format with fewest participants
            formatAssigned = Object.entries(counts).sort((a, b) => a[1] - b[1])[0][0];
        }
        
        // Generate completion code
        const completionCode = `RLHF2026-${uuidv4().split('-')[0].toUpperCase()}`;
        
        // Insert participant
        const stmt = db.prepare(`
            INSERT INTO participants (prolific_pid, format_assigned, design_type, completion_code, started_at)
            VALUES (?, ?, ?, ?, ?)
        `);
        
        const result = stmt.run(prolific_pid, formatAssigned, designType, completionCode, new Date().toISOString());
        const participantId = result.lastInsertRowid;
        
        // For within-subjects, create task assignments
        if (designType === 'within') {
            const annotationsPerFormat = parseInt(db.prepare('SELECT value FROM study_config WHERE key = ?').get('annotations_per_format').value);
            
            // Get random prompts for each format
            const allPrompts = db.prepare('SELECT id FROM prompts ORDER BY RANDOM() LIMIT ?').all(annotationsPerFormat * formatsEnabled.length);
            
            const assignStmt = db.prepare('INSERT INTO task_assignments (participant_id, prompt_id, format) VALUES (?, ?, ?)');
            
            let idx = 0;
            formatsEnabled.forEach(format => {
                for (let i = 0; i < annotationsPerFormat; i++) {
                    assignStmt.run(participantId, allPrompts[idx].id, format);
                    idx++;
                }
            });
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
router.post('/:id/consent', (req, res) => {
    try {
        const { id } = req.params;
        const db = getDb();
        
        db.prepare('UPDATE participants SET consent_given = 1 WHERE id = ?').run(id);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error recording consent:', error);
        res.status(500).json({ error: 'Failed to record consent' });
    }
});

// Record instructions completed
router.post('/:id/instructions', (req, res) => {
    try {
        const { id } = req.params;
        const db = getDb();
        
        db.prepare('UPDATE participants SET instructions_completed = 1 WHERE id = ?').run(id);
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error recording instructions:', error);
        res.status(500).json({ error: 'Failed to record instructions' });
    }
});

// Mark participant as completed
router.post('/:id/complete', (req, res) => {
    try {
        const { id } = req.params;
        const db = getDb();
        
        const participant = db.prepare('SELECT completion_code FROM participants WHERE id = ?').get(id);
        
        if (!participant) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        db.prepare('UPDATE participants SET completed_at = ? WHERE id = ?').run(new Date().toISOString(), id);
        
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
router.get('/:id/progress', (req, res) => {
    try {
        const { id } = req.params;
        const db = getDb();
        
        const participant = db.prepare('SELECT * FROM participants WHERE id = ?').get(id);
        
        if (!participant) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        // Get completion stats
        const completed = db.prepare('SELECT COUNT(*) as cnt FROM annotations WHERE participant_id = ?').get(id).cnt;
        
        let total;
        if (participant.design_type === 'within') {
            total = db.prepare('SELECT COUNT(*) as cnt FROM task_assignments WHERE participant_id = ?').get(id).cnt;
        } else {
            const annotationsPerFormat = parseInt(db.prepare('SELECT value FROM study_config WHERE key = ?').get('annotations_per_format').value);
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
