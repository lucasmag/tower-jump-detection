# Tower Jumps Client

React frontend application for uploading and analyzing cellular carrier data to detect tower jumps.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- `bun` package manager

### Installation

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   bun install
   ```

3. Start the development server:
   ```bash
   bun dev
   ```

   The React app will be available at `http://localhost:5173`

## 🔧 Available Scripts

- `bun dev` - Start development server
- `bun build` - Build for production
- `bun preview` - Preview production build
- `bun lint` - Run ESLint

## 📁 Project Structure

```
client/
├── src/
│   ├── components/          # React components
│   │   ├── FileUpload.jsx   # CSV file upload
│   │   ├── AnalysisResults.jsx # Results display
│   │   └── ProgressTracker.jsx # Progress tracking
│   ├── App.jsx             # Main application
│   └── main.jsx            # Entry point
├── public/                 # Static assets
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## 🌐 Environment Configuration

The app connects to the Flask API server at `http://localhost:5000` by default.

To change the API endpoint, update the base URL in your API calls or set up environment variables.

## 🎨 Features

- CSV file upload with validation
- Real-time analysis progress tracking
- Interactive results visualization
- Export functionality for analysis results
- Responsive design for mobile and desktop