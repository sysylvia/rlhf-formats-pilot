const { getDb, getCurrentExperimentId } = require('../models/db');

// Example prompts for testing
const examplePrompts = [
    {
        text: "Write a haiku about artificial intelligence",
        response_a: "Silicon mind thinks\nData flows through circuits bright\nNew world consciousness",
        response_b: "Machines learn and grow\nAlgorithms dance with grace\nFuture now unfolds",
        response_c: "Digital dreams bloom\nZeros ones create meaning\nSilent wisdom speaks",
        response_d: "Code whispers secrets\nNeural pathways light the way\nIntelligence born",
        source: "test",
        category: "creative"
    },
    {
        text: "Explain photosynthesis to a 10-year-old",
        response_a: "Plants are like tiny factories that use sunlight as energy. They take in carbon dioxide from the air and water from the soil, then use sunlight to turn these into sugar (food for the plant) and oxygen that we breathe.",
        response_b: "Photosynthesis is when plants make their own food using light. They breathe in CO2 and breathe out oxygen, which is great for us! The green stuff in leaves (chlorophyll) captures sunlight and helps turn water and air into energy.",
        response_c: "Think of plants like solar panels. They catch sunlight and use it to cook up their own meals from air and water. As a bonus, they release oxygen into the air - the same oxygen you need to breathe!",
        response_d: "Plants have a superpower - they can make food from sunlight! Their leaves grab light from the sun, suck up water from their roots, and breathe in air. Then they mix it all together to make sugar for energy and release oxygen for us.",
        source: "test",
        category: "factual"
    },
    {
        text: "Should humans colonize Mars?",
        response_a: "Yes, we should colonize Mars. It represents humanity's next great frontier and could serve as a backup for Earth's civilization if catastrophe strikes. The technological advances needed would benefit life on Earth, and the challenge would unite humanity toward a common goal.",
        response_b: "No, we shouldn't colonize Mars until we solve problems on Earth first. The enormous cost could be better spent on climate change, poverty, and healthcare. Mars is inhospitable and terraforming would take centuries, making it an impractical solution to Earth's problems.",
        response_c: "We should pursue Mars colonization carefully and gradually. Start with research stations like Antarctica, not full colonies. Use it to advance space technology and science, but prioritize Earth's well-being. Mars could be valuable long-term, but shouldn't distract from immediate Earth challenges.",
        response_d: "Mars colonization is inevitable and necessary. As technology improves and Earth's resources strain under population growth, Mars offers opportunities for expansion, resource extraction, and scientific discovery. Private companies are already making it economically viable.",
        source: "test",
        category: "reasoning"
    }
];

async function seedPrompts() {
    try {
        console.log('Seeding prompts...');
        
        const pool = getDb();
        const experimentId = await getCurrentExperimentId();
        
        // Check if prompts already exist
        const existingResult = await pool.query(
            'SELECT COUNT(*) as cnt FROM prompts WHERE experiment_id = $1',
            [experimentId]
        );
        
        const existing = parseInt(existingResult.rows[0].cnt);
        
        if (existing > 0) {
            console.log(`⚠️  Experiment ${experimentId} already has ${existing} prompts. Skipping seed.`);
            console.log('To re-seed, delete prompts for this experiment first.');
            return;
        }
        
        const client = await pool.connect();
        
        try {
            await client.query('BEGIN');
            
            for (const p of examplePrompts) {
                await client.query(`
                    INSERT INTO prompts (experiment_id, text, response_a, response_b, response_c, response_d, source, category)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                `, [experimentId, p.text, p.response_a, p.response_b, p.response_c, p.response_d, p.source, p.category]);
            }
            
            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
        
        console.log(`✅ Seeded ${examplePrompts.length} example prompts for experiment ${experimentId}`);
        
    } catch (error) {
        console.error('Error seeding prompts:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    seedPrompts()
        .then(() => process.exit(0))
        .catch((error) => {
            console.error(error);
            process.exit(1);
        });
}

module.exports = { seedPrompts, examplePrompts };
