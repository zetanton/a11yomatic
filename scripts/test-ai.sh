#!/bin/bash
# Test AI service connection

echo "🧪 Testing AI Service Connection"
echo "================================"

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running. Please start it first with ./scripts/dev.sh"
    exit 1
fi

# Test Groq/OpenAI connection
echo "Testing AI service..."
docker-compose exec backend python -c "
import asyncio
from app.services.ai_service import AIService

async def test():
    ai = AIService()
    result = await ai.test_connection()
    if result:
        print('✅ AI service connection successful!')
    else:
        print('❌ AI service connection failed. Please check your API keys.')

asyncio.run(test())
"

echo ""
echo "If the connection failed, please ensure:"
echo "  1. Your API key is set in .env file"
echo "  2. GROQ_API_KEY or OPENAI_API_KEY is configured"
echo "  3. OPENAI_API_BASE_URL is correct (e.g., https://api.groq.com/openai/v1)"


