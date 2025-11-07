# Tower Jumps Server

Flask API server for analyzing cellular carrier data to detect tower jumps (anomalous location changes).

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- `uv` package manager

### Installation

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. Run the Flask server:
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## 📋 API Endpoints

- `POST /upload` - Upload CSV file for analysis
- `POST /analyze` - Start tower jump analysis
- `GET /analysis-status/<job_id>` - Check analysis progress
- `GET /export-csv` - Export analysis results as CSV

## 🧪 Testing

Run the test suite:
```bash
python -m unittest discover tests -v
```

## 📁 Project Structure

```
server/
├── app.py                    # Flask application
├── data_processor.py         # CSV data processing
├── tower_jump_detector.py    # Tower jump detection logic
├── tests/                    # Test suite
│   ├── test_data_processor.py
│   └── test_tower_jump_detector.py
├── pyproject.toml           # Python dependencies
└── README.md               # This file
```

## 🔧 Development

### Code Formatting
```bash
uv run black .
```

### Adding Dependencies
```bash
uv add <package-name>
```

### Development Dependencies
```bash
uv add --dev <package-name>
```