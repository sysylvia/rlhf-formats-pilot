require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { getDb } = require('./models/db');

// Import routes
const participantRoutes = require('./routes/participants');
const annotationRoutes = require('./routes/annotations');
const promptRoutes = require('./routes/prompts');
const studyRoutes = require('./routes/study');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors({
    origin: process.env.FRONTEND_URL || '*',
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
    next();
});

// Health check
app.get('/health', (req, res) => {
    try {
        const db = getDb();
        const result = db.prepare('SELECT 1').get();
        res.json({ 
            status: 'healthy', 
            database: 'connected',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({ 
            status: 'unhealthy', 
            database: 'error',
            error: error.message 
        });
    }
});

// API routes
app.use('/api/participants', participantRoutes);
app.use('/api/annotations', annotationRoutes);
app.use('/api/prompts', promptRoutes);
app.use('/api/study', studyRoutes);

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(500).json({ 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 RLHF Pilot Backend running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, closing server...');
    const { closeDb } = require('./models/db');
    closeDb();
    process.exit(0);
});
