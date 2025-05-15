# Suggestions Service

## Project Overview

The Suggestions Service is an intelligent recommendation system that leverages advanced AI models to provide short personalized suggestions based on user interactions and memories. Built with FastAPI and integrated with multiple AI services, this system offers an approach to understanding user context and generating relevant suggestions across different domains:

### Core Capabilities

1. **Memory-Based Personalization**
   - Maintains a persistent memory of user interactions using Mem0
   - Categorizes memories into 16 distinct domains (personal, professional, lifestyle, etc.)
   - Uses historical context to generate more relevant suggestions

2. **Multi-Modal AI Integration**
   - Automatic model selection based on content type

3. **Smart Context Understanding**
   - Analyzes user conversations and memories
   - Identifies patterns and preferences
   - Maintains user goals and project context

4. **Flexible API Architecture**
   - RESTful endpoints for easy integration
   - Scalable FastAPI backend
   - Comprehensive error handling and validation

### Technical Architecture

The service is structured into several key components:

```
me_app_suggestions/
├── app/                      # Main application directory
│   ├── models/              # Data models and schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Core business logic
│   │   ├── generator.py     # Suggestion generation logic
│   │   └── memory.py        # Memory management service
│   └── main.py             # Application entry point
├── tests/                   # Test suite
└── requirements.txt         # Dependencies
```

### Key Files and Their Purposes

1. **app/main.py**: Application entry point and FastAPI configuration
2. **app/models.py**: Pydantic models for data validation and serialization
3. **app/services/generator.py**: Core suggestion generation logic and model selection
4. **app/services/memory.py**: Memory management and categorization
5. **app/routers/suggestions.py**: API endpoint definitions and request handling
6. **tests/**: Test suite for all components

## Prerequisites

- Python 3.8+
- FastAPI
- LangChain
- Mem0 API access
- OpenAI API access

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/dmitryn2018/me_app_suggestions.git
cd me_app_suggestions
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
MEM0_API_KEY=your_mem0_api_key
OPENAI_PROXY=your_proxy_url  # Optional
```

## API Endpoints

### GET /api/v1/suggestions

Get personalized suggestions based on user's conversation history.

**Parameters:**
- `user_id` (required): The ID of the user to get suggestions for
- `n` (optional): Number of suggestions to return (default: 3, range: 1-10)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions?user_id=test_user&n=3"
```

**Example Response:**
```json
[
  {
    "title": "Optimize Graph Algorithm",
    "description": "Enhance the depth-first search implementation with additional optimizations",
    "model_type": "code",
    "selected_model": "anthropic/claude-3.7-sonnet"
  },
  {
    "title": "Write Technical Blog Post",
    "description": "Create an article about best practices in software development",
    "model_type": "text",
    "selected_model": "gpt-4.1"
  },
  {
    "title": "Design App Logo",
    "description": "Create a modern and minimalist logo for the application",
    "model_type": "image",
    "selected_model": "recraft-ai/recraft-v3-svg"
  }
]
```

## Testing

The project includes comprehensive tests for all components. To run the tests:

```bash
# Install dependencies:
pip install -r requirements-dev.txt

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_suggestions.py

# Run with verbose output
python -m pytest -v

# Run integration tests
python -m pytest tests/test_suggestions_router.py::test_suggestions_with_real_memory
```

## Development

### Project Structure

```
me_app_suggestions/
├── app/
│   ├── models/
│   │   └── suggestions.py
│   ├── services/
│   │   ├── generator.py
│   │   └── memory.py
│   └── main.py
├── tests/
│   ├── test_generator.py
│   ├── test_suggestions.py
│   └── test_suggestions_router.py
├── .env
├── requirements.txt
└── README.md
```
