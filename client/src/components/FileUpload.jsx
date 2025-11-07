import { useState, useRef } from 'react'
import { Upload, FileText, Loader2, AlertCircle, Sparkles } from 'lucide-react'
import axios from 'axios'
import { API_BASE_URL } from '../config'

export default function FileUpload({ onAnalysisComplete, onAnalysisStart, isLoading }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const pollJobStatus = async (jobId, uploadInfo) => {
    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await axios.get(`${API_BASE_URL}/status/${jobId}`)
        const { status, progress, results, error } = statusResponse.data

        setUploadStatus(progress)

        if (status === 'completed') {
          clearInterval(pollInterval)
          setUploadStatus(null)
          onAnalysisComplete({
            summary: results.analysis_summary,
            results: results.results,
            uploadInfo: uploadInfo
          })
        } else if (status === 'failed') {
          clearInterval(pollInterval)
          setError(error || 'Analysis failed. Please try again.')
          setUploadStatus(null)
          onAnalysisComplete(null)
        }
      } catch (err) {
        clearInterval(pollInterval)
        setError('Failed to check analysis status. Please try again.')
        setUploadStatus(null)
        onAnalysisComplete(null)
      }
    }, 3000) // Poll every 3 seconds

    // Clear interval after 10 minutes to prevent indefinite polling
    setTimeout(() => {
      clearInterval(pollInterval)
      if (uploadStatus) {
        setError('Analysis timed out. Please try again.')
        setUploadStatus(null)
        onAnalysisComplete(null)
      }
    }, 5 * 60 * 1000) // 5 minutes timeout
  }

  const handleFileUpload = async (file) => {
    if (!file.name.endsWith('.csv')) {
      setError('Please select a CSV file')
      return
    }

    setError(null)
    onAnalysisStart()

    try {
      // Step 1: Upload the file
      const formData = new FormData()
      formData.append('file', file)

      setUploadStatus('Uploading file...')

      const uploadResponse = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadStatus(`Processing ${uploadResponse.data.records.toLocaleString()} records...`)

      // Step 2: Start the analysis (returns immediately with job ID)
      setUploadStatus('Starting tower jump analysis...')

      const analysisResponse = await axios.post(`${API_BASE_URL}/analyze`)
      const jobId = analysisResponse.data.job_id

      setUploadStatus('Analysis running in background...')

      // Step 3: Poll for results
      await pollJobStatus(jobId, uploadResponse.data)

    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Please try again.')
      setUploadStatus(null)
      onAnalysisComplete(null)
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300 ease-in-out group
          ${isDragOver
            ? 'border-indigo-400 bg-indigo-50/50 scale-[1.02]'
            : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50/50'
          }
          ${isLoading ? 'pointer-events-none' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
          disabled={isLoading}
        />

        <div className="flex flex-col items-center space-y-6">
          {isLoading ? (
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center">
                <Loader2 className="h-8 w-8 text-indigo-600 animate-spin" />
              </div>
              <Sparkles className="h-4 w-4 text-indigo-400 absolute -top-1 -right-1 animate-pulse" />
            </div>
          ) : (
            <div className="relative group-hover:scale-110 transition-transform duration-200">
              <div className="w-16 h-16 rounded-full bg-slate-100 group-hover:bg-indigo-100 flex items-center justify-center transition-colors duration-200">
                <Upload className="h-8 w-8 text-slate-400 group-hover:text-indigo-500 transition-colors duration-200" />
              </div>
            </div>
          )}

          <div className="space-y-2">
            <p className="text-xl font-semibold text-slate-900 tracking-tight">
              {isLoading ? 'Processing Data' : 'Upload CSV File'}
            </p>
            <p className="text-slate-500 font-medium">
              {isLoading
                ? (uploadStatus || 'Analyzing your data...')
                : 'Drag & drop or click to select your carrier data file'
              }
            </p>
          </div>

          {!isLoading && (
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-100 rounded-full">
              <FileText className="h-4 w-4 text-slate-500" />
              <span className="text-xs font-medium text-slate-600">CSV format only</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        </div>
      )}
    </div>
  )
}