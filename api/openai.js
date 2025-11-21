// Vercel Edge Function to proxy OpenAI API requests
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
        const apiKey = process.env.OPENAI_API_KEY;

        if (!apiKey) {
            return res.status(500).json({ error: 'OpenAI API key not configured' });
        }

        // Transform the request body to OpenAI's format
        // Expecting: { messages: [{ role: string, content: string }], model?: string, temperature?: number }
        // Default to GPT-4o (reliable and multimodal)
        const { messages, model = "gpt-4o", temperature = 0.7, max_tokens } = req.body;

        if (!messages || !Array.isArray(messages)) {
            return res.status(400).json({ error: 'Messages array is required' });
        }

        const openaiPayload = {
            model: model,
            messages: messages,
            temperature: temperature
        };

        // Add max_tokens if provided
        if (max_tokens) {
            openaiPayload.max_tokens = max_tokens;
        }

        // Forward the request to OpenAI API
        const openaiResponse = await fetch(
            'https://api.openai.com/v1/chat/completions',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify(openaiPayload)
            }
        );

        if (!openaiResponse.ok) {
            const error = await openaiResponse.text();
            console.error('OpenAI API error:', error);
            return res.status(openaiResponse.status).json({
                error: `OpenAI API error: ${openaiResponse.status}`,
                details: error
            });
        }

        const data = await openaiResponse.json();

        // Transform OpenAI response to match your expected format
        const transformedResponse = {
            text: data.choices?.[0]?.message?.content || '',
            model: data.model,
            usage: data.usage,
            original: data // Include original response for debugging
        };

        return res.status(200).json(transformedResponse);

    } catch (error) {
        console.error('Error proxying to OpenAI:', error);
        return res.status(500).json({
            error: 'Failed to process request',
            details: error.message
        });
    }
}
