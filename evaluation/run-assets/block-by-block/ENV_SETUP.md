# Environment Variables Setup

This document describes how API keys are now managed across the project using environment variables.

## Overview

All API keys have been removed from source code and moved to `.env` files to improve security. The `.env` files are ignored by git and should never be committed to version control.

## Setup Instructions

### 1. Monte Carlo Project

**Location:** `monte_carlo/`

**Required Variables:**
- `MISTRAL_API_KEY` - Mistral AI API key for LLM functionality
- `GOOGLE_API_KEY` - Google API key for search functionality
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID
- `API_PORT` - Server port (default: 5000)

**Setup:**
```bash
cd monte_carlo
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Willow Tree Project

**Location:** `willowtree/`

**Required Variables:**
- `MISTRAL_API_KEY` - Mistral AI API key for financial explanations
- `PORT` - Server port (optional, default: 8000)

**Setup:**
```bash
cd willowtree
cp .env.example .env
# Edit .env and add your API key
```

### 3. Startup Finder Project

**Location:** `startup_finder/`

**Required Variables:**
- `MISTRAL_API_KEY` - Mistral AI API key
- `SERPER_API_KEY` - Serper API key for Google search
- `RAPIDAPI_KEY` - RapidAPI key for LinkedIn data
- `LINKEDIN_COOKIE` - LinkedIn cookie (optional)
- `GEMINI_API_KEY` - Google Gemini API key (optional, legacy)
- `NUM_QUERIES` - Number of search queries (default: 3)
- `MAX_RESULTS_PER_QUERY` - Max results per query (default: 15)
- `TOP_STARTUPS_COUNT` - Number of top startups to return (default: 10)

**Setup:**
```bash
cd startup_finder
# .env already exists with keys, but you can use .env.example as template
cp .env.example .env
# Edit .env and add your API keys
```

## Installation

After setting up your `.env` files, install dependencies:

### Monte Carlo
```bash
cd monte_carlo
uv sync
```

### Willow Tree
```bash
cd willowtree
uv sync
```

### Startup Finder
```bash
cd startup_finder
uv sync
```

## Security Notes

1. **Never commit `.env` files** - They contain sensitive API keys
2. The `.gitignore` file is configured to exclude all `.env` files
3. Use `.env.example` files as templates (with placeholder values)
4. Each project has its own `.env` file for isolation

## Changed Files

### Configuration Files
- `monte_carlo/config.py` - Now loads from environment variables
- `startup_finder/config.py` - Updated test config to use env vars

### Code Files with Hardcoded Keys Removed
- `monte_carlo/search_engine.py`
- `monte_carlo/yahoo_simulation.py`
- `willowtree/server.py`
- `willowtree/advanced_demo.py`
- `willowtree/willowtree/llm_explainer.py`
- `startup_finder/linkedin_profile_analyzer.py`

### New Dependency
- Added `python-dotenv>=1.0.0` to:
  - `monte_carlo/pyproject.toml`
  - `willowtree/pyproject.toml`
  - Already present in `startup_finder/pyproject.toml`

## Migration from Old Code

If you have existing code that used hardcoded API keys:

1. Update to load from environment:
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
```

2. Set up your `.env` file with the actual keys
3. Run `uv sync` to install `python-dotenv` if needed

## Troubleshooting

**Problem:** "API key not found" errors

**Solution:** 
1. Check that your `.env` file exists in the project directory
2. Verify the `.env` file contains the required keys
3. Ensure you're running the code from the correct directory
4. Check that `python-dotenv` is installed (`uv sync`)

**Problem:** Keys still showing in code

**Solution:** Make sure you've pulled the latest changes and that all files have been updated to use `os.getenv()` instead of hardcoded values.
