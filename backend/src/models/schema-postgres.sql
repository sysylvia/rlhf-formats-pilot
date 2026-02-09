-- RLHF Pilot Study Database Schema (PostgreSQL)

-- Experiments table (track multiple studies)
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active', -- 'active', 'paused', 'completed'
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Participants table
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id),
    prolific_pid TEXT NOT NULL,
    format_assigned TEXT NOT NULL, -- 'pairwise', 'bws', 'peer_prediction'
    design_type TEXT NOT NULL, -- 'within' or 'between'
    completion_code TEXT UNIQUE NOT NULL,
    consent_given BOOLEAN DEFAULT FALSE,
    instructions_completed BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(experiment_id, prolific_pid)
);

-- Prompts table (pre-loaded, can be shared across experiments)
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id), -- NULL = shared across experiments
    text TEXT NOT NULL,
    response_a TEXT NOT NULL,
    response_b TEXT NOT NULL,
    response_c TEXT, -- for BWS
    response_d TEXT, -- for BWS
    source TEXT, -- where the prompt came from
    category TEXT, -- type of task (e.g., 'creative', 'factual', 'reasoning')
    created_at TIMESTAMP DEFAULT NOW()
);

-- Annotations table (responses from participants)
CREATE TABLE IF NOT EXISTS annotations (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id),
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    prompt_id INTEGER NOT NULL REFERENCES prompts(id),
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
    created_at TIMESTAMP DEFAULT NOW()
);

-- Task assignments (for within-subjects design)
CREATE TABLE IF NOT EXISTS task_assignments (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id),
    participant_id INTEGER NOT NULL REFERENCES participants(id),
    prompt_id INTEGER NOT NULL REFERENCES prompts(id),
    format TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(experiment_id, participant_id, prompt_id, format)
);

-- Study configuration (per experiment)
CREATE TABLE IF NOT EXISTS study_config (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id),
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(experiment_id, key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_participants_experiment ON participants(experiment_id);
CREATE INDEX IF NOT EXISTS idx_participants_prolific ON participants(prolific_pid);
CREATE INDEX IF NOT EXISTS idx_annotations_experiment ON annotations(experiment_id);
CREATE INDEX IF NOT EXISTS idx_annotations_participant ON annotations(participant_id);
CREATE INDEX IF NOT EXISTS idx_annotations_prompt ON annotations(prompt_id);
CREATE INDEX IF NOT EXISTS idx_annotations_format ON annotations(format);
CREATE INDEX IF NOT EXISTS idx_prompts_experiment ON prompts(experiment_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_experiment ON task_assignments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_participant ON task_assignments(participant_id);

-- Insert default experiment for pilot study
INSERT INTO experiments (name, description, status) 
VALUES ('Pilot Study - Format Comparison', 'Initial pilot comparing pairwise, BWS, and peer prediction formats', 'active')
ON CONFLICT DO NOTHING;

-- Insert default config for experiment 1
INSERT INTO study_config (experiment_id, key, value) VALUES 
    (1, 'design_type', 'within'),
    (1, 'annotations_per_format', '15'),
    (1, 'formats_enabled', 'pairwise,bws,peer_prediction'),
    (1, 'study_active', '1')
ON CONFLICT DO NOTHING;
