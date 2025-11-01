# ASP AI Agent

AI-powered tools and interfaces for antimicrobial stewardship programs.

## Live Demo
- GitHub Pages (Frontend only): https://haslamdb.github.io/asp_ai_agent/
- Full app with API (Vercel): Will be available after deployment

## Features
- **Agent Models**: Test different AI agent models for ASP scenarios
- **ASP AI Agent Interface**: Main application interface for stewardship activities

## Setup Instructions

### Option 1: Deploy to Vercel (Recommended for Full Functionality)

1. **Sign up for Vercel** (if you haven't already):
   - Go to https://vercel.com/signup
   - Sign up with your GitHub account

2. **Import this repository**:
   - Click "Add New Project" in Vercel dashboard
   - Import `haslamdb/asp_ai_agent` repository
   - Configure the project:
     - Framework Preset: Other
     - Root Directory: ./
     - Build Command: (leave empty)
     - Output Directory: (leave empty)

3. **Set up environment variables**:
   - In Vercel project settings, go to "Environment Variables"
   - Add: `GEMINI_API_KEY` with your Google Gemini API key
   - Get a free API key from: https://makersuite.google.com/app/apikey

4. **Deploy**:
   - Click "Deploy"
   - Your app will be available at `https://[your-project-name].vercel.app`

5. **Update the API endpoint**:
   - Edit `agent_models.html` line 170
   - Replace `asp-ai-agent.vercel.app` with your actual Vercel domain

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Create `.env.local` file**:
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env.local
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```
   or
   ```bash
   vercel dev
   ```

4. **Open browser**:
   - Navigate to http://localhost:3000

## Project Structure
```
asp_ai_agent/
├── api/
│   └── gemini.js        # Vercel Edge Function for API proxy
├── agent_models.html    # AI model testing interface
├── asp_ai_agent.html    # Main ASP agent interface
├── index.html           # Landing page
├── vercel.json          # Vercel configuration
├── package.json         # Node dependencies
└── README.md           # This file
```

## Security Notes
- Never commit API keys to the repository
- The API proxy ensures your Gemini API key stays secure on the server
- CORS is configured to only allow requests from authorized origins

## Technologies Used
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Backend**: Vercel Edge Functions
- **AI**: Google Gemini API
- **Hosting**: Vercel (API) + GitHub Pages (static files)

## Contributing
Pull requests are welcome! For major changes, please open an issue first.

## License
This project is proprietary and confidential.