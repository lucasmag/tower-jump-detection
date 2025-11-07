import { useState } from 'react'
import FileUpload from './components/FileUpload'
import Dashboard from './components/Dashboard'

function App() {
  const [analysisResults, setAnalysisResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleAnalysisComplete = (results) => {
    setAnalysisResults(results)
    setIsLoading(false)
  }

  const handleAnalysisStart = () => {
    setIsLoading(true)
    setAnalysisResults(null)
  }

  const handleReset = () => {
    setAnalysisResults(null)
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {!analysisResults && !isLoading && (
          <div className="text-center mb-12 space-y-6">
            <div className="space-y-3">
              <h2 className="text-3xl font-bold text-slate-900 tracking-tight">
                Detect Tower Jumps
              </h2>
              <p className="text-slate-600 max-w-lg mx-auto leading-relaxed">
                Upload cellular carrier data to identify impossible location movements
                and analyze tower triangulation accuracy.
              </p>
            </div>
          </div>
        )}

        <FileUpload
          onAnalysisComplete={handleAnalysisComplete}
          onAnalysisStart={handleAnalysisStart}
          isLoading={isLoading}
        />

        {analysisResults && (
          <Dashboard
            results={analysisResults}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  )
}

export default App
