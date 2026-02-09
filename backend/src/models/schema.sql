-- RLHF Pilot Study Database Schema

-- Participants table
CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prolific_pid TEXT UNIQUE NOT NULL,
    format_assigned TEXT NOT NULL, -- 'pairwise', 'bws', 'peer_prediction'
    design_type TEXT NOT NULL, -- 'within' or 'between'
    completion_code TEXT UNIQUE NOT NULL,
    consent_given INTEGER DEFAULT 0,
    instructions_completed INTEGER DEFAULT 0,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Prompts table (pre-loaded)
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    response_a TEXT NOT NULL,
    response_b TEXT NOT NULL,
    response_c TEXT, -- for BWS
    response_d TEXT, -- for BWS
    source TEXT, -- where the prompt came from
    category TEXT, -- type of task (e.g., 'creative', 'factual', 'reasoning')
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Annotations table (responses from participants)
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    prompt_id INTEGER NOT NULL,
    format TEXT NOT NULL, -- 'pairwise', 'bws', 'peer_prediction'
    
    -- Pairwise fields
    choice TEXT, -- 'A' or 'B'
    confidence REAL, -- 0-100
    
    -- BWS fields
    best_choice TEXT, -- 'A', 'B', 'C', or 'D'
    worst_choice TEXT, -- 'A', 'B', 'C', or 'D'
    
    -- Peer Prediction fields
    own_rating INTEGER, -- 1-5 or 1-7 scale
    predicted_avg REAL, -- what they think others will rate
    confidence_in_prediction REAL, -- 0-100
    
    -- Metadata
    duration_ms INTEGER, -- time to complete annotation
    order_shown INTEGER, -- order in session (1, 2, 3...)
    response_order TEXT, -- randomized order shown (e.g., 'BADC')
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (participant_id) REFERENCES participants(id),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Task assignments (for within-subjects design)
CREATE TABLE IF NOT EXISTS task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    prompt_id INTEGER NOT NULL,
    format TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (participant_id) REFERENCES participants(id),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
    UNIQUE(participant_id, prompt_id, format)
);

-- Study configuration
CREATE TABLE IF NOT EXISTS study_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Insert default config
INSERT OR IGNORE INTO study_config (key, value) VALUES 
    ('design_type', 'within'),
    ('annotations_per_format', '15'),
    ('formats_enabled', 'pairwise,bws,peer_prediction'),
    ('study_active', '1');

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_annotations_participant ON annotations(participant_id);
CREATE INDEX IF NOT EXISTS idx_annotations_prompt ON annotations(prompt_id);
CREATE INDEX IF NOT EXISTS idx_annotations_format ON annotations(format);
CREATE INDEX IF NOT EXISTS idx_task_assignments_participant ON task_assignments(participant_id);
CREATE INDEX IF NOT EXISTS idx_participants_prolific ON participants(prolific_pid);
