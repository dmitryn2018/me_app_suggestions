#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if user_id is provided
if [ -z "$1" ]; then
    echo -e "${RED}Please provide a user_id as parameter${NC}"
    echo "Usage: ./test_api.sh <user_id>"
    echo "Example: ./test_api.sh test_user_123"
    exit 1
fi

USER_ID="$1"
echo -e "${GREEN}Testing Suggestions API for user: ${USER_ID}${NC}\n"

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Test 1: Get suggestions with default parameters
echo -e "${GREEN}Test 1: Get suggestions with default parameters${NC}"
curl -X GET "${BASE_URL}/suggestions?user_id=${USER_ID}" \
  -H "accept: application/json" \
  -w "\nStatus code: %{http_code}\n"

echo -e "\n-----------------------------------\n"

# Test 2: Get suggestions with custom number
echo -e "${GREEN}Test 2: Get suggestions with custom number (n=20)${NC}"
curl -X GET "${BASE_URL}/suggestions?user_id=${USER_ID}&n=20" \
  -H "accept: application/json" \
  -w "\nStatus code: %{http_code}\n"

echo -e "\n-----------------------------------\n"

# Test 3: Test invalid n parameter
echo -e "${GREEN}Test 3: Test invalid n parameter (n=21)${NC}"
curl -X GET "${BASE_URL}/suggestions?user_id=${USER_ID}&n=11" \
  -H "accept: application/json" \
  -w "\nStatus code: %{http_code}\n"

echo -e "\n-----------------------------------\n"

# Test 4: Test missing user_id
echo -e "${GREEN}Test 4: Test missing user_id${NC}"
curl -X GET "${BASE_URL}/suggestions" \
  -H "accept: application/json" \
  -w "\nStatus code: %{http_code}\n"

echo -e "\n-----------------------------------\n"

# Test 5: Get suggestions with pretty-printed output
echo -e "${GREEN}Test 5: Get suggestions with pretty-printed output${NC}"
curl -X GET "${BASE_URL}/suggestions?user_id=${USER_ID}" \
  -H "accept: application/json" | python -m json.tool

echo -e "\n-----------------------------------\n" 