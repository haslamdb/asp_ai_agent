// Vercel Edge Function to proxy Claude/Anthropic API requests
export default async function handler(req, res) {
    // Enable CORS for your GitHub Pages site
    const allowedOrigins = [
        'https://haslamdb.github.io',
        'http://localhost:3000',
        'http://127.0.0.1:5500', // For local development
        'http://localhost:5000'  // Local Python server
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
        const apiKey = process.env.ANTHROPIC_API_KEY;
        
        if (!apiKey) {
            return res.status(500).json({ error: 'Claude API key not configured' });
        }
        
        // Transform the request body to Claude's format
        // Expecting: { system: string, messages: [{ role: string, content: string }], max_tokens?: number }
        const { system, messages, max_tokens = 4000, model = "claude-3-5-sonnet-20241022" } = req.body;
        
        if (!messages || !Array.isArray(messages)) {
            return res.status(400).json({ error: 'Messages array is required' });
        }
        
        const claudePayload = {
            model: model,
            max_tokens: max_tokens,
            messages: messages
        };
        
        // Add system message if provided
        if (system) {
            claudePayload.system = system;
        }
        
        // Forward the request to Claude API
        const claudeResponse = await fetch(
            'https://api.anthropic.com/v1/messages',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify(claudePayload)
            }
        );
        
        if (!claudeResponse.ok) {
            const error = await claudeResponse.text();
            console.error('Claude API error:', error);
            return res.status(claudeResponse.status).json({ 
                error: `Claude API error: ${claudeResponse.status}`,
                details: error
            });
        }
        
        const data = await claudeResponse.json();
        
        // Transform Claude response to match your expected format
        const transformedResponse = {
            text: data.content?.[0]?.text || '',
            model: data.model,
            usage: data.usage,
            original: data // Include original response for debugging
        };
        
        return res.status(200).json(transformedResponse);
        
    } catch (error) {
        console.error('Error proxying to Claude:', error);
        return res.status(500).json({ 
            error: 'Failed to process request',
            details: error.message 
        });
    }
}