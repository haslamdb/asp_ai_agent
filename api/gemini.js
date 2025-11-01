// Vercel Edge Function to proxy Gemini API requests
export default async function handler(req, res) {
    // Enable CORS for your GitHub Pages site
    const allowedOrigins = [
        'https://haslamdb.github.io',
        'http://localhost:3000',
        'http://127.0.0.1:5500' // For local development
    ];
    
    const origin = req.headers.origin;
    if (allowedOrigins.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
    }
    
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        // Get the API key from environment variable (set in Vercel dashboard)
        const apiKey = process.env.GEMINI_API_KEY;
        
        if (!apiKey) {
            return res.status(500).json({ error: 'API key not configured' });
        }
        
        // Forward the request to Gemini API
        const geminiResponse = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(req.body)
            }
        );
        
        if (!geminiResponse.ok) {
            const error = await geminiResponse.text();
            return res.status(geminiResponse.status).json({ 
                error: `Gemini API error: ${error}` 
            });
        }
        
        const data = await geminiResponse.json();
        return res.status(200).json(data);
        
    } catch (error) {
        console.error('Error proxying to Gemini:', error);
        return res.status(500).json({ 
            error: 'Failed to process request',
            details: error.message 
        });
    }
}