#!/bin/bash

# Define green and red color for echo
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create and Activate Virtual Environment
echo -e "${GREEN}[Step 1] Creating and activating virtual environment...${NC}"
if [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "Linux" ]; then
    python3 -m venv w2m
    echo -e "${GREEN}Activating virtual environment (bin/activate)${NC}"
    source w2m/bin/activate
else
    python -m venv w2m
    echo -e "${GREEN}Activating virtual environment (Scripts/activate)${NC}"
    source w2m/Scripts/activate
fi

# Install Dependencies
echo -e "${GREEN}[Step 2] Installing backend dependencies from requirements.txt...${NC}"
cd "Django Code Base"
pip install -r requirements.txt
cd ..

echo -e "${GREEN}[Step 3] Installing frontend dependencies with npm...${NC}"
cd Frontend
npm install
cd ..

echo -e "${GREEN}[Step 4] Installing iOS pods if ios directory exists...${NC}"
if [ -d "ios" ]; then
    cd ios
    pod install
    cd ..
fi

# Setup Server
echo -e "${GREEN}[Step 5] Setting up Django server scripts...${NC}"
cd "Django Code Base"
chmod +x *.sh
if [ -f setup-local-postgres.sh ]; then
    echo -e "${GREEN}Running setup-local-postgres.sh...${NC}"
    ./setup-local-postgres.sh
fi