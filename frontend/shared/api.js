// API client for RLHF Pilot Backend

const API_BASE_URL = window.API_BASE_URL || 'https://rlhf-formats-pilot-production.up.railway.app/api';

class PilotAPI {
    // Participants
    static async registerParticipant(prolificPid) {
        const response = await fetch(`${API_BASE_URL}/participants/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prolific_pid: prolificPid })
        });
        return await response.json();
    }
    
    static async recordConsent(participantId) {
        const response = await fetch(`${API_BASE_URL}/participants/${participantId}/consent`, {
            method: 'POST'
        });
        return await response.json();
    }
    
    static async recordInstructions(participantId) {
        const response = await fetch(`${API_BASE_URL}/participants/${participantId}/instructions`, {
            method: 'POST'
        });
        return await response.json();
    }
    
    static async completeParticipant(participantId) {
        const response = await fetch(`${API_BASE_URL}/participants/${participantId}/complete`, {
            method: 'POST'
        });
        return await response.json();
    }
    
    static async getProgress(participantId) {
        const response = await fetch(`${API_BASE_URL}/participants/${participantId}/progress`);
        return await response.json();
    }
    
    // Annotations
    static async submitAnnotation(data) {
        const response = await fetch(`${API_BASE_URL}/annotations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await response.json();
    }
    
    static async getNextTask(participantId) {
        const response = await fetch(`${API_BASE_URL}/annotations/next/${participantId}`);
        return await response.json();
    }
    
    // Study
    static async getConfig() {
        const response = await fetch(`${API_BASE_URL}/study/config`);
        return await response.json();
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PilotAPI;
}
