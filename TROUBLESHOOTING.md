# OmniSupply - Troubleshooting Guide

This guide covers common issues and their solutions.

---

## 🔧 Package Management Issues

### Error: `ModuleNotFoundError: No module named 'openai.types.chat'`

**Cause**: Corrupted OpenAI package installation in uv-managed environment

**Solution**:
```bash
# Resync environment to fix corrupted packages
uv sync

# Verify fix
python -c "from openai import OpenAI; print('✅ Fixed')"
```

### Error: `No module named 'XYZ'`

**Solution**:
```bash
# If using uv (recommended):
uv sync

# If using pip:
pip install -r requirements.txt
```

---

## 🗄️ Database Issues

### Error: `Connection refused` or timeout when connecting to PostgreSQL

**Cause**: PostgreSQL is not running or wrong connection settings

**Solution**:
```bash
# Check if PostgreSQL container is running
docker ps | grep omnisupply-postgres

# If not running, start it:
docker start omnisupply-postgres

# If container doesn't exist, run setup:
bash setup_local_postgres.sh

# Verify .env configuration:
cat .env | grep POSTGRES
```

### Error: `Database session error` during data loading

**Cause**: Large dataset timing out on remote server

**Solution**:
```bash
# Use local PostgreSQL instead of remote
bash setup_local_postgres.sh

# Update .env:
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=omnisupply
POSTGRES_PASSWORD=omnisupply123
POSTGRES_DB=omnisupply

# Load data
python load_full_data.py
```

### Error: `column "is_returned" is of type integer but expression is of type boolean`

**Cause**: Schema type mismatch after migration

**Solution**:
```bash
# Run migration script
python migrate_is_returned_auto.py

# Or manually:
# ALTER TABLE omnisupply.orders ALTER COLUMN is_returned TYPE BOOLEAN;
```

---

## 🤖 Agent Issues

### Error: `operator does not exist: integer = boolean`

**Cause**: PostgreSQL boolean column queried with wrong syntax

**Solution**: This should be fixed in all agent files. If you encounter this:
1. Check the query uses `CASE WHEN boolean_col THEN 1 ELSE 0 END` for aggregation
2. Not using `SUM(boolean_col)` directly

### Error: `OPENAI_API_KEY not found`

**Solution**:
```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Verify
cat .env | grep OPENAI_API_KEY
```

---

## 📊 Data Loading Issues

### Issue: "Data loading is stuck" or taking too long

**Causes**:
1. Remote PostgreSQL server (slow connection)
2. Large dataset (180K+ orders)

**Solutions**:

**Option 1: Use local PostgreSQL** (recommended)
```bash
bash setup_local_postgres.sh
# Update .env to use localhost
python load_full_data.py  # Loads in ~15 seconds
```

**Option 2: Use smaller dataset for testing**
```bash
python quick_demo_small_data.py  # Loads only 10K orders
```

### Issue: Validation shows "102 issues found" for inventory

**This is EXPECTED** - the sample inventory data has all items with `stock_quantity = 0`, which triggers validation warnings. This is not a bug.

---

## 🐳 Docker Issues

### Error: `Docker not found`

**Solution**:
```bash
# Install Docker Desktop
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Linux: https://docs.docker.com/engine/install/
# Windows: https://docs.docker.com/desktop/install/windows-install/
```

### Error: `Container already exists`

**Solution**:
```bash
# Remove old container
docker stop omnisupply-postgres
docker rm omnisupply-postgres

# Re-run setup
bash setup_local_postgres.sh
```

---

## 💻 Python Environment Issues

### Error: `python: command not found` or wrong Python version

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.11+

# If wrong version, install Python 3.11+
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

### Issue: Using wrong virtual environment

**Solution**:
```bash
# Deactivate any active environment
deactivate

# If using uv (recommended):
uv sync

# If using venv:
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

---

## 🔍 Debugging Tips

### Check system status

```bash
# 1. Verify Python environment
python --version
which python

# 2. Verify PostgreSQL is running
docker ps | grep postgres

# 3. Verify database has data
python -c "
from src.storage.sql.database import DatabaseClient
import os
from dotenv import load_dotenv
load_dotenv()
db_url = f'postgresql://{os.getenv(\"POSTGRES_USER\")}:{os.getenv(\"POSTGRES_PASSWORD\")}@{os.getenv(\"POSTGRES_HOST\")}:{os.getenv(\"POSTGRES_PORT\")}/{os.getenv(\"POSTGRES_DB\")}'
db = DatabaseClient(database_url=db_url)
print(db.get_table_counts())
db.close()
"

# 4. Verify OpenAI API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API key loaded' if os.getenv('OPENAI_API_KEY') else '❌ No API key')"
```

### Enable verbose logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check agent execution

```bash
# Test individual agent
python -c "
from src.agents import DataAnalystAgent
from src.storage.sql.database import DatabaseClient
import os
from dotenv import load_dotenv

load_dotenv()
db_url = f'postgresql://{os.getenv(\"POSTGRES_USER\")}:{os.getenv(\"POSTGRES_PASSWORD\")}@{os.getenv(\"POSTGRES_HOST\")}:{os.getenv(\"POSTGRES_PORT\")}/{os.getenv(\"POSTGRES_DB\")}'
db = DatabaseClient(database_url=db_url)
agent = DataAnalystAgent(db_client=db)
result = agent.execute('Count total orders')
print(f'Success: {result.success}')
print(f'Insights: {result.insights[0] if result.insights else \"None\"}')
db.close()
"
```

---

## 📦 UV vs PIP

This project uses **uv** for package management. Here's a comparison:

| Task | uv | pip |
|------|-----|-----|
| Install all dependencies | `uv sync` | `pip install -r requirements.txt` |
| Add new package | `uv add <pkg>` | `pip install <pkg>` |
| Remove package | `uv remove <pkg>` | `pip uninstall <pkg>` |
| Update packages | `uv sync --upgrade` | `pip install -U -r requirements.txt` |
| Lock dependencies | Automatic (uv.lock) | Manual (pip freeze > requirements.txt) |

**Why uv?**
- ⚡ 10-100x faster than pip
- 🔒 Reproducible builds with uv.lock
- 🎯 Better dependency resolution
- 📦 Single command to setup environment

---

## 🆘 Getting Help

If you encounter an issue not covered here:

1. Check the error message carefully
2. Review [SESSION_COMPLETION_SUMMARY.md](SESSION_COMPLETION_SUMMARY.md) for implementation details
3. Search GitHub issues: https://github.com/yourusername/OmniSupply/issues
4. Create a new issue with:
   - Error message (full traceback)
   - Python version (`python --version`)
   - uv version (`uv --version`)
   - Steps to reproduce

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
# Full system health check
python -c "
import sys
print(f'Python: {sys.version}')

from openai import OpenAI
print('✅ OpenAI import')

from src.storage.sql.database import DatabaseClient
import os
from dotenv import load_dotenv
load_dotenv()

db_url = f'postgresql://{os.getenv(\"POSTGRES_USER\")}:{os.getenv(\"POSTGRES_PASSWORD\")}@{os.getenv(\"POSTGRES_HOST\")}:{os.getenv(\"POSTGRES_PORT\")}/{os.getenv(\"POSTGRES_DB\")}'
db = DatabaseClient(database_url=db_url)
counts = db.get_table_counts()
print(f'✅ Database: {sum(counts.values()):,} records')

from src.agents import DataAnalystAgent
agent = DataAnalystAgent(db_client=db)
print(f'✅ Agent: {agent.name}')

db.close()
print('\\n🎉 All systems operational!')
"
```

---

**Last Updated**: December 6, 2025
