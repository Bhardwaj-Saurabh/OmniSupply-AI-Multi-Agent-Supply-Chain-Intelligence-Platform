# Setup Guide: Data Analyst Agent with Opik Observability

## Prerequisites
- Python 3.11+
- OpenAI API key
- Comet.com account (for Opik)

---

## Step 1: Clone & Navigate
```bash
cd OmniSupply-AI-Multi-Agent-Supply-Chain-Intelligence-Platform
```

## Step 2: Install Dependencies

### Option A: Using uv (Recommended - Fast)
```bash
uv sync
```

### Option B: Using pip
```bash
pip install -e .
```

This will install all dependencies from `pyproject.toml`:
- LangChain & LangGraph
- OpenAI SDK
- Opik for observability
- DuckDB for SQL queries
- Plotly for visualizations
- scikit-learn for anomaly detection
- ChromaDB for vector storage

---

## Step 3: Set Up Opik (Comet)

### 3.1 Create Comet Account
1. Go to [https://www.comet.com/signup](https://www.comet.com/signup)
2. Sign up for a free account
3. Navigate to **Settings → API Keys**
4. Copy your API key

### 3.2 Create Opik Project
```bash
# Install Opik CLI (if needed)
pip install opik

# Initialize Opik
opik init
```

This will:
- Prompt for your Comet API key
- Create a configuration file
- Set up your workspace

### 3.3 Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Fill in:
```
OPENAI_API_KEY=sk-proj-...
COMET_API_KEY=your-comet-api-key
COMET_WORKSPACE=your-workspace-name
OPIK_PROJECT_NAME=omnisupply-data-analyst
```

---

## Step 4: Verify Data Files

Ensure your data files are in the `data/` directory:
```bash
ls -lh data/
```

Expected files:
- `DataCoSupplyChainDataset.csv` (96 MB)
- `dynamic_supply_chain_logistics_dataset.csv` (15 MB)
- `supply_chain_data.csv` (21 KB)
- `Retail-Supply-Chain-Sales-Dataset.xlsx` (1.5 MB)

---

## Step 5: Test Opik Integration

Create a test script to verify Opik is working:

**File**: `test_opik.py`
```python
from opik import track
import opik

# Initialize Opik
client = opik.Opik()

@track(project_name="omnisupply-data-analyst")
def test_tracking():
    """Test Opik tracking"""
    return {"status": "success", "message": "Opik is working!"}

if __name__ == "__main__":
    result = test_tracking()
    print(result)
    print("\n✅ Check your Comet workspace for traces!")
    print("🔗 https://www.comet.com/your-workspace/projects/omnisupply-data-analyst")
```

Run the test:
```bash
python test_opik.py
```

You should see the trace in your Comet dashboard!

---

## Step 6: Run the Research Notebook

```bash
jupyter notebook notebooks/research.ipynb
```

This will:
- Load all 4 datasets
- Show data analysis and feasibility assessment
- Verify data is ready for the agent

---

## Step 7: Verify Installation

Create a quick verification script:

**File**: `verify_setup.py`
```python
import sys

def check_imports():
    """Verify all required packages are installed"""
    required = [
        'langchain',
        'langgraph',
        'openai',
        'pandas',
        'duckdb',
        'plotly',
        'sklearn',
        'opik',
        'chromadb',
    ]

    print("Checking dependencies...\n")
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT FOUND")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -e .")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def check_env():
    """Check environment variables"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    print("\nChecking environment variables...\n")

    required_env = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'COMET_API_KEY': 'Comet API key for Opik',
    }

    missing_env = []
    for key, desc in required_env.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {key} - Set ({desc})")
        else:
            print(f"❌ {key} - NOT SET ({desc})")
            missing_env.append(key)

    if missing_env:
        print(f"\n⚠️  Missing env vars: {', '.join(missing_env)}")
        print("Edit your .env file")
        return False
    else:
        print("\n✅ All environment variables set!")
        return True

def check_data():
    """Check data files exist"""
    import os

    print("\nChecking data files...\n")

    data_files = [
        'data/DataCoSupplyChainDataset.csv',
        'data/dynamic_supply_chain_logistics_dataset.csv',
        'data/supply_chain_data.csv',
        'data/Retail-Supply-Chain-Sales-Dataset.xlsx',
    ]

    missing_data = []
    for file_path in data_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"✅ {file_path} ({size_mb:.1f} MB)")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            missing_data.append(file_path)

    if missing_data:
        print(f"\n⚠️  Missing data files: {', '.join(missing_data)}")
        return False
    else:
        print("\n✅ All data files present!")
        return True

if __name__ == "__main__":
    print("="*60)
    print("OmniSupply AI Setup Verification")
    print("="*60 + "\n")

    checks = [
        check_imports(),
        check_env(),
        check_data(),
    ]

    print("\n" + "="*60)
    if all(checks):
        print("🎉 Setup Complete! Ready to build the Data Analyst Agent!")
        print("="*60)
        print("\nNext steps:")
        print("1. Review IMPLEMENTATION_PLAN.md")
        print("2. Start with Phase 1: Project structure")
        print("3. Run: python -m src.agents.data_analyst.agent")
    else:
        print("❌ Setup incomplete. Fix the issues above.")
        print("="*60)
        sys.exit(1)
```

Run verification:
```bash
python verify_setup.py
```

---

## Step 8: Opik Dashboard Overview

Once everything is set up, you'll see these features in Opik:

### 1. Traces View
- See every agent execution
- Drill down into each node (parse → SQL → visualize)
- View LLM inputs/outputs
- Track token usage and latency

### 2. Experiments
- Compare different prompts
- A/B test models (GPT-4 vs GPT-4o-mini)
- Track metric improvements over time

### 3. Datasets
- Store test queries and expected outputs
- Run regression tests automatically
- Version your evaluation datasets

### 4. Evaluations
- Hallucination detection scores
- Answer relevance metrics
- Custom metrics (SQL accuracy, chart quality)

### 5. Feedback
- Collect user feedback on responses
- Correlate feedback with trace data
- Identify areas for improvement

---

## Troubleshooting

### Issue: Opik not logging traces
**Solution**:
```bash
# Check Opik configuration
opik config show

# Reinitialize if needed
opik init --force
```

### Issue: Import errors
**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -e .

# Or with uv
uv sync --reinstall
```

### Issue: OpenAI API errors
**Solution**:
```bash
# Verify API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:20])"

# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list().data[0].id)"
```

### Issue: Data encoding errors
**Solution**:
The loader in `src/data/loader.py` handles this automatically by trying multiple encodings (utf-8, latin-1, iso-8859-1, cp1252).

---

## What's Next?

Now that setup is complete, follow the implementation plan:

1. **Phase 1**: Create directory structure
2. **Phase 2**: Implement data loading with DuckDB
3. **Phase 3**: Build LangGraph agent core
4. **Phase 4**: Add tools (SQL, stats, charts)
5. **Phase 5**: Configure prompts
6. **Phase 6**: Test with example queries
7. **Phase 7**: Enable Opik tracking

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed steps!

---

## Useful Commands

```bash
# Install dependencies
uv sync

# Run tests
pytest tests/

# Start Jupyter
jupyter notebook

# Run agent (after implementation)
python -m src.agents.data_analyst.agent --query "Show me sales trends"

# View Opik traces
open https://www.comet.com/your-workspace/projects/omnisupply-data-analyst
```

---

## Resources

- [Opik Documentation](https://www.comet.com/docs/opik/)
- [Opik LangChain Integration](https://www.comet.com/docs/opik/tracing/integrations/langchain/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/tutorials/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview)

---

**Happy Building! 🚀**
