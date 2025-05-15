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
