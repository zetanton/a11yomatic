# Custom AI Service Configuration
## A11yomatic - PDF Accessibility Remediation Tool

### 1. Overview

A11yomatic supports custom AI services as an alternative to the default OpenAI API. This allows you to use your own AI infrastructure, self-hosted models, or third-party AI services that are compatible with the OpenAI API format.

### 2. Supported AI Service Types

#### 2.1 OpenAI-Compatible Services
- **OpenAI API**: Default service (api.openai.com)
- **Groq API**: Fast inference service (api.groq.com)
- **Azure OpenAI**: Microsoft's OpenAI service
- **Local OpenAI-Compatible APIs**: Self-hosted solutions
- **Third-party OpenAI-Compatible Services**: Services like Together AI, Replicate, etc.

#### 2.2 Custom AI Endpoints
- **Self-hosted LLMs**: Ollama, vLLM, Text Generation Inference
- **Cloud AI Services**: AWS Bedrock, Google Vertex AI, etc.
- **Custom API Endpoints**: Any REST API that follows OpenAI's format

### 3. Configuration

#### 3.1 Environment Variables

**Required Variables:**
```bash
# Your AI service API key
OPENAI_API_KEY=your-api-key-here

# Custom API base URL (optional, defaults to OpenAI)
OPENAI_API_BASE_URL=https://your-custom-ai-service.com/v1

# Groq API key (for fast inference)
GROQ_API_KEY=your-groq-api-key-here
```

**Example Configurations:**

**OpenAI API (Default):**
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

**Groq API (Fast Inference):**
```bash
OPENAI_API_KEY=gsk_your-groq-key
OPENAI_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_API_KEY=gsk_your-groq-key
```

**Azure OpenAI:**
```bash
OPENAI_API_KEY=your-azure-key
OPENAI_API_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
```

**Local Ollama:**
```bash
OPENAI_API_KEY=ollama
OPENAI_API_BASE_URL=http://localhost:11434/v1
```

**Custom AI Service:**
```bash
OPENAI_API_KEY=your-custom-key
OPENAI_API_BASE_URL=https://your-ai-service.com/api/v1
```

#### 3.2 Docker Configuration

**Docker Compose Setup:**
```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL:-https://api.openai.com/v1}
```

**Environment File (.env):**
```bash
# Copy from env.example and update
cp env.example .env

# Edit .env file
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE_URL=https://your-custom-ai-service.com/v1
```

### 4. Implementation Details

#### 4.1 Backend Configuration

**Settings Configuration:**
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # AI Services
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE_URL: str = "https://api.openai.com/v1"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**AI Service Implementation:**
```python
# backend/app/services/ai_service.py
import openai
from app.core.config import settings

class AIService:
    def __init__(self):
        # Configure OpenAI client with custom base URL
        openai.api_base = settings.OPENAI_API_BASE_URL
        openai.api_key = settings.OPENAI_API_KEY
    
    async def generate_content(self, prompt: str, model: str = "gpt-3.5-turbo"):
        """Generate content using configured AI service"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                api_base=settings.OPENAI_API_BASE_URL,
                api_key=settings.OPENAI_API_KEY
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise
```

#### 4.2 API Compatibility

**Required Endpoints:**
Your custom AI service must support the following OpenAI-compatible endpoints:

```
POST /v1/chat/completions
POST /v1/completions
POST /v1/models
```

**Request Format:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "user", "content": "Generate alt text for this image: [description]"}
  ],
  "max_tokens": 150,
  "temperature": 0.3
}
```

**Response Format:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Generated content here"
      }
    }
  ]
}
```

### 5. Popular AI Service Setups

#### 5.1 Groq API (Recommended for Development)

**Configuration:**
```bash
OPENAI_API_KEY=gsk_your-groq-key
OPENAI_API_BASE_URL=https://api.groq.com/openai/v1
GROQ_API_KEY=gsk_your-groq-key
```

**Benefits:**
- Extremely fast inference (up to 750 tokens/second)
- Cost-effective for development
- OpenAI-compatible API
- Multiple model options (Llama, Mixtral, etc.)
- Free tier available

**Getting Started:**
1. Sign up at [console.groq.com](https://console.groq.com)
2. Generate an API key
3. Configure the environment variables above
4. Start using with fast inference

#### 5.2 Azure OpenAI

**Configuration:**
```bash
OPENAI_API_KEY=your-azure-key
OPENAI_API_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
```

**Benefits:**
- Enterprise-grade security
- Azure integration
- Compliance certifications
- Custom model fine-tuning

#### 5.2 Local Ollama

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

**Configuration:**
```bash
OPENAI_API_KEY=ollama
OPENAI_API_BASE_URL=http://localhost:11434/v1
```

**Benefits:**
- Complete privacy
- No API costs
- Offline operation
- Custom model support

#### 5.3 AWS Bedrock

**Configuration:**
```bash
OPENAI_API_KEY=your-aws-access-key
OPENAI_API_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com
```

**Benefits:**
- AWS integration
- Multiple model providers
- Enterprise features
- Scalable infrastructure

#### 5.4 Google Vertex AI

**Configuration:**
```bash
OPENAI_API_KEY=your-google-credentials
OPENAI_API_BASE_URL=https://us-central1-aiplatform.googleapis.com/v1
```

**Benefits:**
- Google Cloud integration
- Advanced AI capabilities
- Enterprise support
- Custom model training

### 6. Testing Your Configuration

#### 6.1 Health Check

**Test API Connection:**
```python
# Test script
import openai
from app.core.config import settings

async def test_ai_service():
    try:
        openai.api_base = settings.OPENAI_API_BASE_URL
        openai.api_key = settings.OPENAI_API_KEY
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ AI service is working!")
        return True
    except Exception as e:
        print(f"❌ AI service error: {e}")
        return False
```

#### 6.2 Docker Test

**Test with Docker:**
```bash
# Start services
docker-compose up -d

# Test AI service
docker-compose exec backend python -c "
from app.services.ai_service import AIService
import asyncio
asyncio.run(AIService().test_connection())
"
```

### 7. Troubleshooting

#### 7.1 Common Issues

**Connection Errors:**
- Check API base URL format
- Verify API key is correct
- Ensure service is running
- Check network connectivity

**Authentication Errors:**
- Verify API key format
- Check key permissions
- Ensure key is not expired
- Validate service credentials

**Model Errors:**
- Check model name is correct
- Verify model is available
- Check model permissions
- Validate model parameters

#### 7.2 Debug Mode

**Enable Debug Logging:**
```bash
# In .env file
LOG_LEVEL=DEBUG
AI_DEBUG=true
```

**View AI Service Logs:**
```bash
# Docker logs
docker-compose logs -f backend

# Specific AI service logs
docker-compose exec backend tail -f /app/logs/ai_service.log
```

### 8. Performance Optimization

#### 8.1 Caching

**Response Caching:**
```python
# Cache AI responses to reduce API calls
@cache.memoize(timeout=3600)  # 1 hour cache
async def generate_cached_content(prompt: str):
    return await ai_service.generate_content(prompt)
```

#### 8.2 Rate Limiting

**Implement Rate Limiting:**
```python
# Rate limit AI requests
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)  # 60 calls per minute
async def rate_limited_ai_call(prompt: str):
    return await ai_service.generate_content(prompt)
```

#### 8.3 Fallback Strategy

**Multiple AI Services:**
```python
class AIServiceWithFallback:
    def __init__(self):
        self.primary_service = AIService(settings.OPENAI_API_BASE_URL)
        self.fallback_service = AIService(settings.FALLBACK_API_BASE_URL)
    
    async def generate_content(self, prompt: str):
        try:
            return await self.primary_service.generate_content(prompt)
        except Exception:
            return await self.fallback_service.generate_content(prompt)
```

### 9. Security Considerations

#### 9.1 API Key Security

**Secure Storage:**
- Use environment variables
- Never commit keys to version control
- Rotate keys regularly
- Use key management services

**Network Security:**
- Use HTTPS for API calls
- Implement request signing
- Use VPN for internal services
- Monitor API usage

#### 9.2 Data Privacy

**Data Handling:**
- Review data retention policies
- Implement data encryption
- Use local models for sensitive data
- Audit data access

### 10. Monitoring and Analytics

#### 10.1 Usage Tracking

**Track AI Service Usage:**
```python
# Monitor AI service calls
class AIServiceMonitor:
    def __init__(self):
        self.call_count = 0
        self.total_tokens = 0
        self.error_count = 0
    
    async def track_call(self, prompt: str, response: str):
        self.call_count += 1
        self.total_tokens += len(prompt) + len(response)
```

#### 10.2 Cost Monitoring

**Track API Costs:**
```python
# Monitor API costs
class CostTracker:
    def __init__(self):
        self.total_cost = 0.0
        self.cost_per_token = 0.0001  # Example rate
    
    def calculate_cost(self, tokens: int):
        cost = tokens * self.cost_per_token
        self.total_cost += cost
        return cost
```

This configuration allows you to use any OpenAI-compatible AI service with A11yomatic, providing flexibility in choosing the best AI solution for your needs while maintaining the same interface and functionality.
