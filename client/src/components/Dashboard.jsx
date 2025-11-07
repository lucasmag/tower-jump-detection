import { useState } from 'react'
import { Download, AlertTriangle, CheckCircle, RotateCcw, Map, Table, Activity, TrendingUp, Zap } from 'lucide-react'
import ResultsTable from './ResultsTable'
import LocationMap from './LocationMap'
import ConfidenceIndicator from './ConfidenceIndicator'
import axios from 'axios'
import { API_BASE_URL } from '../config'

export default function Dashboard({ results, onReset }) {
  const [activeView, setActiveView] = useState('table')
  const [isExporting, setIsExporting] = useState(false)

  if (!results) return null

  const { summary, results: analysisResults, uploadInfo } = results

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/export`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'tower_jumps_analysis.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="space-y-8 mt-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Analysis Results</h2>
        <p className="text-slate-600">Tower jump detection completed successfully</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60 hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Total Periods</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {(summary?.total_periods || 0).toLocaleString()}
              </p>
            </div>
            <div className="h-12 w-12 bg-indigo-100 rounded-xl flex items-center justify-center">
              <Activity className="h-6 w-6 text-indigo-600" />
            </div>
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60 hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Tower Jumps</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {(summary?.tower_jumps_detected || 0).toLocaleString()}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {summary?.tower_jump_percentage || 0}% of periods
              </p>
            </div>
            <div className="h-12 w-12 bg-red-100 rounded-xl flex items-center justify-center">
              <Zap className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60 hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Avg Confidence</p>
              <p className="text-2xl font-bold text-emerald-600 mt-1">
                {summary?.avg_confidence || 0}%
              </p>
            </div>
            <div className="h-12 w-12 bg-emerald-100 rounded-xl flex items-center justify-center">
              <CheckCircle className="h-6 w-6 text-emerald-600" />
            </div>
          </div>
        </div>

        <div className="bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60 hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600">Max Speed</p>
              <p className="text-2xl font-bold text-amber-600 mt-1">
                {(summary?.max_speed_detected || 0).toLocaleString()}
              </p>
              <p className="text-xs text-slate-500 mt-1">km/h detected</p>
            </div>
            <div className="h-12 w-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-amber-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Info */}
      <div className="bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60">
        <h3 className="text-lg font-semibold text-slate-900 mb-6 tracking-tight">Dataset Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-600">Records Processed</p>
            <p className="text-lg font-semibold text-slate-900">
              {(uploadInfo?.records || 0).toLocaleString()}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-600">Date Range</p>
            <p className="text-sm text-slate-700 font-medium">
              {uploadInfo?.date_range ?
                `${new Date(uploadInfo.date_range.start).toLocaleDateString()} - ${new Date(uploadInfo.date_range.end).toLocaleDateString()}`
                : 'Loading...'
              }
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-slate-600">States Covered</p>
            <p className="text-sm text-slate-700 font-medium">
              {summary?.states_involved ? `${summary.states_involved.length} states` : 'Loading...'}
            </p>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-center bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60">
        <div className="flex bg-slate-100 rounded-xl p-1 mb-4 sm:mb-0">
          <button
            onClick={() => setActiveView('table')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
              activeView === 'table'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Table className="h-4 w-4" />
            <span>Table</span>
          </button>
          <button
            onClick={() => setActiveView('map')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
              activeView === 'map'
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Map className="h-4 w-4" />
            <span>Map</span>
          </button>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-xl transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="h-4 w-4" />
            <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
          </button>
          <button
            onClick={onReset}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white text-sm font-medium rounded-xl transition-colors duration-200"
          >
            <RotateCcw className="h-4 w-4" />
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {/* Results Display */}
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-slate-200/60 overflow-hidden">
        {activeView === 'table' && <ResultsTable />}
        {activeView === 'map' && <LocationMap results={analysisResults} />}
      </div>
    </div>
  )
}