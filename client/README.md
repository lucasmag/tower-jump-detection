# Tower Jumps Client

React frontend application for uploading and analyzing cellular carrier data to detect tower jumps.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- `bun` package manager (fast JavaScript runtime and package manager)

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
│   │   ├── FileUpload.jsx   # CSV file upload with drag-and-drop
│   │   ├── Dashboard.jsx    # Main results dashboard
│   │   ├── ResultsTable.jsx # Data table with sorting/filtering
│   │   └── ConfidenceIndicator.jsx # Confidence level display
│   ├── App.jsx             # Main application with state management
│   ├── config.js           # API configuration
│   └── main.jsx            # Entry point
├── public/                 # Static assets
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## 🌐 Environment Configuration

The app connects to the Flask API server at `http://localhost:5000` by default.

To change the API endpoint, update the `API_BASE_URL` in `src/config.js`:

```javascript
export const API_BASE_URL = 'http://localhost:5000/api'
```