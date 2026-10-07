# Block by Block AI Odyssey 🚀

A comprehensive financial AI toolkit featuring quantitative trading models, derivative pricing, Monte Carlo simulations, startup discovery, and advanced stock prediction models. This repository contains multiple interconnected projects for financial analysis, algorithmic trading, and investment research.

## 📋 Table of Contents

- [Overview](#overview)
- [Projects](#projects)
  - [Double Auction - Multi-Agent Trading](#double-auction---multi-agent-trading-simulation)
  - [RL Model - Reinforcement Learning Trading](#rl-model---reinforcement-learning-trading)
  - [Monte Carlo - Jump Diffusion Simulator](#monte-carlo---jump-diffusion-simulator)
  - [Willow Tree - Derivatives Pricing](#willow-tree---derivatives-pricing)
  - [Startup Finder - Investment Discovery](#startup-finder---investment-discovery)
  - [Stock Transformer - Time Series Prediction](#stock-transformer---time-series-prediction)
  - [Block by Block Frontend](#block-by-block-frontend)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🎯 Overview

This repository is a complete financial AI ecosystem that combines:

- **Multi-Agent Systems**: Competitive self-play in continuous double auction markets
- **Machine Learning**: Deep reinforcement learning (PPO) for algorithmic trading
- **Quantitative Finance**: Monte Carlo simulations, jump-diffusion models, derivatives pricing
- **AI Analysis**: LLM-powered market analysis, news interpretation, and startup evaluation
- **Modern Web Stack**: React + TypeScript frontend with real-time data visualization
- **Investment Research**: Automated startup discovery and analysis across industries

## 🏗️ Projects

### Double Auction - Multi-Agent Trading Simulation

**Location:** `double_auction-master/`

A sophisticated multi-agent reinforcement learning (MARL) environment simulating a continuous double auction (CDA) market where multiple AI agents compete as traders in a limit order book.

**Key Features:**
- Multi-agent competitive self-play trading environment
- Continuous double auction (CDA) with limit order book
- Real market data integration (AAPL, NVDA, NEE, TSLA)
- PPO (Proximal Policy Optimization) agents with competitive training
- Order book simulation with bids/asks across multiple price levels
- Complex action space: market/limit orders, cancel, modify
- Synthetic order book generation from OHLCV data
- Backtesting on real historical market data
- RLlib integration for distributed training

**Technology Stack:**
- Ray RLlib for multi-agent RL
- PyTorch for neural networks
- OpenAI Gym/Gymnasium for environment
- yfinance for market data
- TensorBoard for training visualization
- NumPy, pandas for data processing

**Quick Start:**
```bash
cd double_auction-master

# Install dependencies
pip install -e .
# Or with uv:
uv sync

# Train agents on simulated environment
python main.py

# Train on real market data (AAPL, NEE)
python train_real_market.py

# Test trained agents on unseen data
python test_real_trained_model.py
```

**What It Does:**
1. **Simulated Environment Training**:
   - Creates synthetic limit order book with multiple agents
   - Agents learn through competitive self-play
   - Winning agent's policy weights are copied to other agents
   - Reward maximizes profit while minimizing number of trades

2. **Real Market Training**:
   - Fetches historical OHLCV data from yfinance
   - Converts real prices into synthetic order books
   - Trains PPO agents on actual market dynamics
   - Evaluates on unseen test tickers (e.g., TSLA)

3. **Order Book Mechanics**:
   - 10-level depth order book (configurable)
   - Bid/Ask spread calculated from market data
   - Order sizes based on volume
   - All agents see same order book snapshot (equal lag)

**Action Space:**
- **Action Type**: No action, Buy, Sell (3 options)
- **Order Type**: Market, Limit, Cancel, Modify (4 options)
- **Price Adjustment**: Continuous [-1.0, 1.0] relative to best bid/ask
- **Quantity Ratio**: Continuous [0.0, 1.0] of available capital
- **Tick Size**: Discrete [0-11] price multiplier

**Observation Space:**
- 4×10 matrix representing order book:
  - Row 0: Bid sizes (quantities)
  - Row 1: Bid prices
  - Row 2: Ask sizes (quantities)
  - Row 3: Ask prices

**Training Configuration:**
```python
Training Iterations: 100 (real market) / 200 (simulated)
Batch Size: 4096 samples
Learning Rate: 1e-4 (real market) / 3e-4 (simulated)
Workers: 2 parallel environments
Gamma: 0.95 (real market) / 0.99 (simulated)
```

**Files:**
- `main.py` - Complete training pipeline with backtesting
- `train_real_market.py` - Train on real market data
- `test_real_trained_model.py` - Test trained agents
- `gym_continuousDoubleAuction/` - Core environment
  - `envs/continuousDoubleAuction_env.py` - CDA environment
  - `train_on_real_data.py` - Real market wrapper
  - `test_on_real_data.py` - Testing utilities
  - `run_backtest.py` - Backtesting engine

**Results:**
- Trained agents achieve profitability against random agents
- Competitive self-play improves strategy robustness
- Real market testing validates learned policies
- TensorBoard visualization of training progress

**Documentation:**
- `README.md` - Original project documentation
- `REAL_MARKET_TRAINING.md` - Real market training guide
- Jupyter notebooks for experiments (`CDA_NSP_FIXED.ipynb`)

---

### RL Model - Reinforcement Learning Trading

**Location:** `RL_model/`

A sophisticated algorithmic trading system using FinRL (Financial Reinforcement Learning) with Proximal Policy Optimization (PPO) for automated stock trading decisions.

**Key Features:**
- PPO-based trading agent trained on historical market data
- Real-time trading signals and portfolio management
- Custom trading environments with realistic market simulation
- Live backtesting and performance metrics
- Flask API for model predictions

**Technology Stack:**
- FinRL, Stable-Baselines3, PyTorch
- Flask, yfinance, pandas, numpy
- Jupyter notebooks for training

**Quick Start:**
```bash
cd RL_model

# Install dependencies
pip install -r requirements_server.txt

# Run the trading server
python server.py
# Server runs on http://localhost:5000

# Open dashboard
open dashboard.html
```

**What It Does:**
1. Fetches real-time stock data from Yahoo Finance
2. Processes data with technical indicators (MACD, RSI, CCI, ADX)
3. Uses trained PPO model to generate trading actions (buy/sell/hold)
4. Provides trading signals with confidence scores
5. Backtests strategies and visualizes performance

**Files:**
- `server.py` - Main Flask API server
- `config.py` - Configuration and parameters
- `data_utils.py` - Data fetching and preprocessing
- `environments.py` - Trading environment implementations
- `model_utils.py` - Model loading and prediction
- `FinRL_BlockByBlock.ipynb` - Training notebook
- `dashboard.html` - Trading dashboard UI

---

### Monte Carlo - Jump Diffusion Simulator

**Location:** `monte_carlo/`

Advanced Monte Carlo simulation engine for modeling stock price dynamics with jump-diffusion processes, incorporating news-driven jump analysis and AI-powered market interpretation.

**Key Features:**
- Merton jump-diffusion Monte Carlo simulations
- News-based jump event detection and analysis
- 48-hour price jump prediction using AI
- Real-time market sentiment analysis
- Google search integration for news correlation
- Web crawling for financial articles

**Technology Stack:**
- FastAPI, uvicorn
- Mistral AI for market analysis
- yfinance for market data
- scipy for statistical modeling
- crawl4ai for web scraping

**Quick Start:**
```bash
cd monte_carlo

# Set up environment
cp .env.example .env
# Edit .env and add your API keys

# Install dependencies
uv sync

# Run the server
uv run server.py
# Server runs on http://localhost:5000
```

**API Endpoints:**
- `POST /simulate` - Run full Monte Carlo simulation with jump analysis
- `POST /predict` - Get 48-hour jump probability prediction
- `POST /news` - Analyze specific date for news-driven jumps
- `GET /health` - Server health check

**What It Does:**
1. Estimates jump-diffusion parameters from historical data
2. Runs Monte Carlo simulations to forecast price distributions
3. Detects historical jump events (large price movements)
4. Correlates jumps with news events using web search
5. Uses Mistral AI to interpret simulation results
6. Predicts future jump probabilities

**Environment Variables:**
- `MISTRAL_API_KEY` - Mistral AI API key
- `GOOGLE_API_KEY` - Google Custom Search API key
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID
- `API_PORT` - Server port (default: 5000)

---

### Willow Tree - Derivatives Pricing

**Location:** `willowtree/`

Python implementation of Michael Curran's Willow Tree lattice model for efficient derivatives pricing, enhanced with AI-powered financial explanations.

**Key Features:**
- Fast and accurate European/American option pricing
- Barrier options, Asian options, lookback options
- Greeks calculation (delta, gamma, vega, theta, rho)
- Real-time market data integration with yfinance
- AI-powered explanations using Mistral AI
- What-if scenario analysis
- FastAPI REST API

**Technology Stack:**
- NumPy, SciPy for numerical computations
- Matplotlib, Seaborn for visualizations
- Mistral AI for natural language explanations
- FastAPI for API server
- yfinance for market data

**Quick Start:**
```bash
cd willowtree

# Set up environment
cp .env.example .env
# Edit .env and add MISTRAL_API_KEY

# Install dependencies
uv sync

# Run the server
uv run server.py
# Server runs on http://localhost:8000

# Test the API
python test_api.py

# Run advanced demo
python advanced_demo.py
```

**API Endpoints:**
- `POST /price/european` - Price European options
- `POST /price/american` - Price American options
- `POST /price/barrier` - Price barrier options
- `POST /greeks` - Calculate option Greeks
- `POST /what-if` - Run scenario analysis
- `GET /health` - Server health check

**What It Does:**
1. Builds efficient Willow Tree lattice for modeling Brownian motion
2. Prices various derivative contracts (calls, puts, barriers, exotics)
3. Calculates Greeks for risk management
4. Fetches real-time market data for options
5. Provides AI explanations in multiple styles (beginner/intermediate/expert)
6. Enables what-if analysis for parameter sensitivity

**Documentation:**
- `README.md` - Quick start guide
- `API_DOCUMENTATION.md` - Complete API reference
- `TECHNICAL_DEEP_DIVE.md` - Mathematical foundations

---

### Startup Finder - Investment Discovery

**Location:** `startup_finder/`

AI-powered startup discovery and analysis engine that identifies promising startups in any industry using web search, LinkedIn data, and comprehensive AI analysis.

**Key Features:**
- Industry-specific startup discovery using optimized search
- Multi-source data extraction (Crunchbase, LinkedIn, TechCrunch)
- Team analysis via LinkedIn profiles
- Funding and traction metrics
- AI-powered startup evaluation using Mistral
- Investment report generation
- REST API for integration

**Technology Stack:**
- LangChain for AI workflows
- Mistral AI for analysis
- Serper API for Google search
- RapidAPI for LinkedIn data
- FastAPI for API server
- python-dotenv for configuration

**Quick Start:**
```bash
cd startup_finder

# Set up environment (already exists with keys)
cp .env.example .env
# Edit .env and add your API keys

# Install dependencies
uv sync

# Find startups in an industry
python main.py "quantum computing"

# With custom parameters
python main.py "AI healthcare" --queries 5 --results 20 --top 10

# Run API server
python api_server.py
# Server runs on http://localhost:8001
```

**API Endpoints:**
- `POST /analyze-industry` - Analyze an industry and find startups
- `POST /search-startups` - Search for startups by industry
- `POST /enrich-startup` - Get detailed startup information
- `GET /health` - Server health check

**What It Does:**
1. Generates optimized search queries for industry + startup keywords
2. Searches web using Serper API (Google Search)
3. Extracts startup information from multiple sources
4. Enriches data with LinkedIn company profiles
5. Analyzes founding teams and key personnel
6. Evaluates funding, traction, and market position
7. Generates comprehensive investment reports with recommendations

**Environment Variables:**
- `MISTRAL_API_KEY` - Mistral AI for analysis
- `SERPER_API_KEY` - Serper for Google search
- `RAPIDAPI_KEY` - RapidAPI for LinkedIn data
- `LINKEDIN_COOKIE` - LinkedIn session (optional)
- `GEMINI_API_KEY` - Google Gemini (legacy, optional)

**Output:**
- JSON reports saved to `industry_reports/`
- Startup details saved to `startup_results/`
- Comprehensive analysis with scoring and recommendations

---

### Stock Transformer - Time Series Prediction

**Location:** `stock_transformer/`

Advanced stock price prediction using Transformer neural networks for time-series forecasting.

**Structure:**
```
stock_transformer/
├── Model_training/
│   ├── download_stock_data.py  # Data acquisition
│   ├── Transformer.ipynb        # Model training notebook
│   └── Input file/              # Training data
└── server/                      # Prediction API server
```

**Key Features:**
- Transformer architecture for temporal dependencies
- Multi-step ahead forecasting
- Technical indicator integration
- Model training pipeline
- Prediction API

**Quick Start:**
```bash
cd stock_transformer/Model_training

# Download stock data
python download_stock_data.py

# Train model (use Jupyter notebook)
jupyter notebook Transformer.ipynb
```

**What It Does:**
1. Downloads historical stock data
2. Preprocesses and engineers features
3. Trains Transformer model on time series
4. Generates multi-day price forecasts
5. Serves predictions via API

---

### Block by Block Frontend

**Location:** `block-by-block-frontend/`

Modern React + TypeScript frontend for visualizing trading data, Monte Carlo simulations, and financial analysis.

**Key Features:**
- Real-time data visualization with Recharts
- Responsive design with Tailwind CSS
- Interactive trading dashboards
- Monte Carlo simulation results
- Option pricing visualizations
- Startup analysis display

**Technology Stack:**
- React 19, TypeScript
- Vite for fast development
- Recharts for data visualization
- Tailwind CSS for styling
- Lucide React for icons

**Quick Start:**
```bash
cd block-by-block-frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Opens on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

**What It Does:**
1. Connects to backend APIs (RL Model, Monte Carlo, Willow Tree)
2. Displays real-time trading signals and portfolio performance
3. Visualizes Monte Carlo simulation results
4. Shows option pricing curves and Greeks
5. Renders startup analysis reports

**Scripts:**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

---

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.10+ (3.13 recommended for monte_carlo and willowtree)
- **Node.js**: 16+ (for frontend)
- **uv**: Python package manager (recommended) - [Install uv](https://github.com/astral-sh/uv)

### API Keys Required

You'll need API keys for full functionality:

1. **Mistral AI** (Required for AI features)
   - Get at: https://console.mistral.ai/
   - Used in: monte_carlo, willowtree, startup_finder

2. **Google Custom Search** (Optional - for Monte Carlo news analysis)
   - Get API key at: https://console.cloud.google.com/
   - Create Custom Search Engine at: https://cse.google.com/
   - Used in: monte_carlo

3. **Serper API** (Required for startup_finder)
   - Get at: https://serper.dev/
   - Used in: startup_finder

4. **RapidAPI** (Optional - for LinkedIn data in startup_finder)
   - Get at: https://rapidapi.com/
   - Subscribe to LinkedIn Data API
   - Used in: startup_finder

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/AbderrazagB/block-by-block-ai-odyssey.git
cd block-by-block-ai-odyssey
```

### 2. Set Up Python Projects

Each Python project can be set up independently:

```bash
# Double Auction
cd double_auction-master
pip install -e .
# Or with uv:
uv sync

# Monte Carlo
cd ../monte_carlo
cp .env.example .env
# Edit .env with your API keys
uv sync
uv run server.py

# Willow Tree
cd ../willowtree
cp .env.example .env
# Edit .env with your API keys
uv sync
uv run server.py

# Startup Finder
cd ../startup_finder
# .env already exists with keys, but you can copy from example
uv sync
python api_server.py

# RL Model
cd ../RL_model
pip install -r requirements_server.txt
python server.py
```

### 3. Set Up Frontend

```bash
cd block-by-block-frontend
npm install
npm run dev
```

### 4. Access Services

- **Double Auction**: Run locally (no server, training pipeline)
- **RL Trading Server**: http://localhost:5000
- **Monte Carlo API**: http://localhost:5000 (or configured port)
- **Willow Tree API**: http://localhost:8000
- **Startup Finder API**: http://localhost:8001
- **Frontend**: http://localhost:5173

## 🔐 Environment Setup

All API keys are stored in `.env` files (git-ignored for security).

### Monte Carlo (.env)
```bash
MISTRAL_API_KEY=your_mistral_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_custom_search_engine_id
API_PORT=5000
```

### Willow Tree (.env)
```bash
MISTRAL_API_KEY=your_mistral_api_key
PORT=8000
```

### Startup Finder (.env)
```bash
MISTRAL_API_KEY=your_mistral_api_key
SERPER_API_KEY=your_serper_api_key
RAPIDAPI_KEY=your_rapidapi_key
LINKEDIN_COOKIE=your_linkedin_cookie_optional
GEMINI_API_KEY=your_gemini_api_key_optional
NUM_QUERIES=3
MAX_RESULTS_PER_QUERY=15
TOP_STARTUPS_COUNT=10
```

**Important:** 
- Never commit `.env` files to git
- Use `.env.example` files as templates
- Each project has its own `.env` file
- `.gitignore` is configured to exclude all `.env` files

See [ENV_SETUP.md](ENV_SETUP.md) for detailed environment configuration.

## 📊 Architecture

```
block-by-block-ai-odyssey/
│
├── double_auction-master/        # Multi-agent CDA trading
│   ├── main.py                   # Complete training pipeline
│   ├── train_real_market.py      # Real market training
│   ├── test_real_trained_model.py # Model testing
│   └── gym_continuousDoubleAuction/
│       ├── envs/                 # CDA environment
│       ├── train/                # Training utilities
│       └── test/                 # Testing utilities
│
├── RL_model/                     # Reinforcement learning trading
│   ├── server.py                # Flask API
│   ├── model_utils.py           # PPO model
│   └── dashboard.html           # Trading UI
│
├── monte_carlo/              # Jump-diffusion simulator
│   ├── server.py            # FastAPI server
│   ├── jump_diffusion.py    # Monte Carlo engine
│   ├── jump_predictor.py    # AI prediction
│   └── news_service.py      # News analysis
│
├── willowtree/              # Derivatives pricing
│   ├── server.py           # FastAPI server
│   └── willowtree/         # Core library
│       ├── american.py     # American options
│       ├── european.py     # European options
│       └── llm_explainer.py # AI explanations
│
├── startup_finder/          # Investment discovery
│   ├── api_server.py       # FastAPI server
│   ├── startup_search_extractor.py
│   ├── rapidapi_analyzer.py
│   └── config.py           # Configuration
│
├── stock_transformer/       # Time series prediction
│   ├── Model_training/     # Training pipeline
│   └── server/            # Prediction API
│
├── block-by-block-frontend/ # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API clients
│   │   └── types/        # TypeScript types
│   └── package.json
│
├── .gitignore             # Git ignore rules
├── ENV_SETUP.md          # Environment guide
└── README.md             # This file
```

## 🔗 API Integration Flow

```
Frontend (React)
    ↓
    ├─→ RL Model API (Trading signals)
    ├─→ Monte Carlo API (Simulations)
    ├─→ Willow Tree API (Options pricing)
    └─→ Startup Finder API (Investment research)
         ↓
    Backend Services
         ↓
    ├─→ Yahoo Finance (Market data)
    ├─→ Mistral AI (Analysis)
    ├─→ Google Search (News)
    └─→ RapidAPI (LinkedIn data)
```

## 🧪 Testing

Each project includes testing utilities:

```bash
# Test Double Auction environment
cd double_auction-master
python main.py  # Full training + backtesting pipeline
python test_real_trained_model.py  # Test on TSLA data

# Test Monte Carlo API
cd monte_carlo
curl -X POST http://localhost:5000/simulate \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "period": "1y"}'

# Test Willow Tree API
cd willowtree
python test_api.py

# Test Startup Finder
cd startup_finder
python main.py "fintech" --queries 2 --top 3

# Test RL Model
cd RL_model
python test_server.py
```

## 📦 Dependencies Management

This project uses **uv** for fast, reliable Python dependency management:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (instead of pip install)
uv sync

# Run scripts with uv
uv run server.py

# Add new dependency
uv add package-name

# Update dependencies
uv lock --upgrade
```

For projects without `pyproject.toml`, use traditional pip:
```bash
pip install -r requirements.txt
```

## 🛠️ Development Workflow

### Adding a New Feature

1. **Choose the right project** based on functionality
2. **Update environment variables** if needed
3. **Modify code** in the relevant files
4. **Test locally** using test scripts
5. **Update documentation** (README, API docs)
6. **Commit changes** with descriptive messages

### Common Tasks

**Start all backend services:**
```bash
# Terminal 1 - Double Auction Training
cd double_auction-master && python main.py

# Terminal 2 - RL Model
cd RL_model && python server.py

# Terminal 3 - Monte Carlo
cd monte_carlo && uv run server.py

# Terminal 4 - Willow Tree
cd willowtree && uv run server.py

# Terminal 5 - Startup Finder
cd startup_finder && python api_server.py

# Terminal 6 - Frontend
cd block-by-block-frontend && npm run dev
```

**Update all dependencies:**
```bash
cd double_auction-master && pip install -e . --upgrade
cd ../monte_carlo && uv lock --upgrade && uv sync
cd ../willowtree && uv lock --upgrade && uv sync
cd ../startup_finder && uv lock --upgrade && uv sync
cd ../RL_model && pip install -r requirements_server.txt --upgrade
cd ../block-by-block-frontend && npm update
```

## 📚 Additional Resources

### Project-Specific Documentation
- [Double Auction README](double_auction-master/README.md) - Environment and training
- [Double Auction Real Market Guide](double_auction-master/REAL_MARKET_TRAINING.md) - Real market training
- [Monte Carlo README](monte_carlo/README.md) - API endpoints and usage
- [Willow Tree README](willowtree/README.md) - Mathematical theory
- [Willow Tree API Docs](willowtree/API_DOCUMENTATION.md) - Complete API reference
- [Willow Tree Technical Deep Dive](willowtree/TECHNICAL_DEEP_DIVE.md) - Implementation details
- [Startup Finder README](startup_finder/README.md) - Search and analysis guide
- [Startup Finder API Docs](startup_finder/API_DOCUMENTATION.md) - API reference
- [RL Model README](RL_model/README_REFACTORED.md) - Refactored architecture
- [Environment Setup](ENV_SETUP.md) - Detailed environment configuration

### External Resources
- [FinRL Documentation](https://github.com/AI4Finance-Foundation/FinRL)
- [Ray RLlib Documentation](https://docs.ray.io/en/latest/rllib/index.html)
- [Mistral AI Docs](https://docs.mistral.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Use ESLint configuration provided
- **Commits**: Use clear, descriptive commit messages

## 📄 License

This project is part of an AI/ML odyssey and is provided as-is for educational and research purposes.

## 🙏 Acknowledgments

- **FinRL** - Foundation for reinforcement learning trading
- **Ray RLlib** - Multi-agent reinforcement learning framework
- **Continuous Double Auction Environment** - Original by ChuaCheowHuan
- **Willow Tree** - Original implementation by Federico Maria Massari
- **Mistral AI** - LLM capabilities for market analysis
- **FastAPI** - Modern API framework
- **React & Vite** - Frontend framework and tooling

## 📞 Support

For questions or issues:
1. Check project-specific READMEs
2. Review [ENV_SETUP.md](ENV_SETUP.md) for configuration issues
3. Check API documentation for each service
4. Open an issue on GitHub

---
