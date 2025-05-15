# Testing the Suggestions API with curl

This guide explains how to test the Suggestions API endpoints using curl commands.

## Prerequisites

1. The API server must be running locally on port 8000
2. curl must be installed on your system
3. Python 3.x (for pretty-printing JSON responses)
4. A valid user ID (required for most endpoints)

## Starting the Server

Before running the tests, start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

## Running the Tests

You can either run individual curl commands or use the provided test script:

### Using the Test Script

The test script requires a user ID as a parameter:

```bash
./test_api.sh <user_id>
```

Example:
```bash
./test_api.sh test_user_123
```

This will run all test cases with formatted output for the specified user.

### Manual Testing with curl

1. Get suggestions with default parameters:
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions?user_id=test_user_123" \
  -H "accept: application/json"
```

2. Get suggestions with custom number:
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions?user_id=test_user_123&n=2" \
  -H "accept: application/json"
```

3. Test invalid n parameter:
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions?user_id=test_user_123&n=11" \
  -H "accept: application/json"
```

4. Test missing user_id:
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions" \
  -H "accept: application/json"
```

5. Get suggestions with pretty-printed output:
```bash
curl -X GET "http://localhost:8000/api/v1/suggestions?user_id=test_user_123" \
  -H "accept: application/json" | python -m json.tool
```

## API Parameters

### Required Parameters:
- `user_id` (string): The ID of the user to get suggestions for. This is required for most endpoints and is used to retrieve user-specific memories and generate personalized suggestions.

### Optional Parameters:
- `n` (integer, default=3): Number of suggestions to return. Must be between 1 and 10.

## Expected Responses

1. Successful response (200 OK):
```json
[
  {
    "title": "Optimize your algorithm",
    "description": "Improve the time complexity of your graph traversal algorithm",
    "model_type": "code",
    "selected_model": "anthropic/claude-3.7-sonnet"
  },
  {
    "title": "Create a modern logo",
    "description": "Design a minimalist tech startup logo",
    "model_type": "image",
    "selected_model": "openai/gpt-image-1"
  }
]
```

2. Validation error (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["query", "n"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

3. Server error (500 Internal Server Error):
```json
{
  "detail": "Error generating suggestions: ..."
}
```

## Troubleshooting

1. If you get "Connection refused":
   - Make sure the FastAPI server is running on port 8000
   - Check if there are any firewall issues

2. If you get "Invalid JSON":
   - The response might be an HTML error page
   - Check the server logs for errors
   - Verify the API endpoint URL is correct

3. If you get unexpected suggestions:
   - Verify the user_id has associated memories
   - Check the memory service logs
   - Verify the suggestion generator configuration

4. If you get a 422 error:
   - Check that the user_id is provided
   - Verify that n is between 1 and 10
   - Ensure all required parameters are properly formatted 