# Tower Jumps Detection System

A Python + React application for detecting "tower jumps" in cellular carrier data - situations where cell tower triangulation shows impossible rapid movements between locations.

## Project Structure

```
towerjumps/
├── server/          # Python Flask backend
│   ├── app.py                     # Main Flask application
│   ├── data_processor.py          # CSV data processing
│   ├── tower_jump_detector.py     # Detection algorithm
│   ├── tests/                     # Test suite
│   ├── pyproject.toml             # Python dependencies (uv)
│   └── README.md                  # Server documentation
├── client/          # React frontend (Vite + Tailwind)
│   ├── src/
│   │   ├── components/             # React components
│   │   └── App.jsx                 # Main app component
│   ├── package.json                # Node dependencies (bun)
│   └── README.md                   # Client documentation
├── docker-compose.yml              # Docker setup
├── README.md                       # This file
└── tower_jumps_analysis_result.csv # Report result
```

## Features

### Backend (Python Flask)
- **Data Processing**: Handles CSV upload and preprocessing with data validation
- **Tower Jump Detection**:
  - Velocity analysis (flags movements >1000km/h - aircraft speed threshold)
  - State boundary crossing detection with frequency analysis
  - Time-window clustering (30-minute periods)
  - Multi-factor confidence scoring (0-100%)
  - NY/CT specific pattern detection
- **RESTful API**: Upload, analyze, export functionality with background job processing

### Frontend (React + Vite + Tailwind)
- **File Upload**: Drag-and-drop CSV upload with progress tracking
- **Interactive Dashboard**:
  - Summary statistics cards
  - Sortable results table with filtering
  - Interactive map visualization using Leaflet
  - Confidence level indicators
- **Export**: Download analysis results as CSV
- **Responsive Design**: Mobile-friendly interface

## Getting Started

### 🐳 Quick Start with Docker (Recommended)

**Prerequisites:** Docker and Docker Compose installed and running

```bash
# Clone and navigate to project
cd towerjumps

# Build and start both services
docker compose up --build

# Or run in background
docker compose up -d --build
```

**Access the application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/health

**Stop the services:**
```bash
docker compose down
```

> **Note:** If Docker isn't available, use the development setup below.

### 📝 Development Setup (Local)

For detailed setup instructions, see the individual README files:

- **Backend Setup**: See [`server/README.md`](server/README.md)
- **Frontend Setup**: See [`client/README.md`](client/README.md)

## Usage

1. **Upload Data**: Drag and drop your carrier data CSV file or click to browse
2. **Analysis**: The system automatically processes the file and runs tower jump detection
3. **View Results**:
   - See summary statistics (total periods, tower jumps detected, confidence levels)
   - Browse detailed results in table format
   - Visualize locations on an interactive map
4. **Export**: Download the analysis results as a CSV file

### Output Format
Each analysis period includes:
- Time range (start/end)
- Primary state location
- Tower jump indicator (True/False)
- Confidence level (0-100%)
- Maximum speed detected
- Number of state changes
- Record count

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload CSV file for analysis
- `POST /api/analyze` - Start tower jump analysis (returns job ID)
- `GET /api/status/<job_id>` - Check analysis progress and results
- `GET /api/results` - Get analysis results
- `GET /api/export` - Export analysis results as CSV

## Technology Stack

- **Backend**: Python 3.12+, Flask, pandas, numpy, geopy, uv package manager, black code formatting
- **Frontend**: React, Vite, Tailwind CSS, Leaflet, bun package manager
- **Data Processing**: pandas for CSV handling, geopy for distance calculations
- **Testing**: unittest
- **Development**: Docker Compose for containerization
