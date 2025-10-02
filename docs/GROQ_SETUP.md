# Groq API Setup Guide

## Quick Setup for Groq (Fast AI Inference)

Groq provides extremely fast AI inference (up to 750 tokens/second) and is perfect for development and testing.

### 1. Get Your Groq API Key

1. **Sign up**: Go to [console.groq.com](https://console.groq.com)
2. **Create account**: Sign up with your email
3. **Generate API key**: Go to API Keys section and create a new key
4. **Copy the key**: It will look like `gsk_...`

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file
nano .env
```

**Add to your .env file:**
```bash
# Groq API Configuration
OPENAI_API_KEY=gsk_your-groq-key-here
OPENAI_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_API_KEY=gsk_your-groq-key-here
```

### 3. Start the Application

```bash
# Start with Docker Compose
docker-compose up -d

# Or use the setup script
./scripts/dev.sh
```

### 4. Test Your Configuration

```bash
# Test Groq connection
docker-compose exec backend python -c "
from app.services.ai_service import AIService
import asyncio
asyncio.run(AIService().test_connection())
"
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Groq Benefits

- **Speed**: Up to 750 tokens/second
- **Cost**: Very affordable for development
- **Models**: Llama 2, Mixtral, Gemma
- **Free Tier**: Available for testing
- **OpenAI Compatible**: Drop-in replacement

## Available Models

- `llama2-70b-4096`: Large, high-quality responses
- `mixtral-8x7b-32768`: Fast, efficient model
- `gemma-7b-it`: Good balance of speed and quality

## Troubleshooting

### Common Issues

1. **Invalid API Key**: Check your key format (should start with `gsk_`)
2. **Rate Limits**: Groq has generous limits, but check your usage
3. **Model Not Found**: Ensure you're using supported model names

### Debug Mode

Enable debug logging:
```bash
# In .env file
LOG_LEVEL=DEBUG
AI_DEBUG=true
```

View logs:
```bash
docker-compose logs -f backend
```

## Cost Information

- **Free Tier**: 14,400 requests per day
- **Paid Plans**: Very affordable pricing
- **Speed**: Much faster than traditional APIs
- **Perfect for**: Development, testing, and rapid prototyping

## Next Steps

1. Set up your Groq API key
2. Configure the environment
3. Start the application
4. Begin testing PDF accessibility features with fast AI inference!

For detailed configuration options, see [Custom AI Setup Guide](docs/custom-ai-setup.md).

