import { useState, useEffect } from 'react'
import { ChevronUp, ChevronDown, AlertTriangle, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react'
import ConfidenceIndicator from './ConfidenceIndicator'
import axios from 'axios'
import { API_BASE_URL } from '../config'

export default function ResultsTable() {
  const [results, setResults] = useState([])
  const [pagination, setPagination] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sortConfig, setSortConfig] = useState({ key: 'TimeStart', direction: 'asc' })
  const [filterTowerJumps, setFilterTowerJumps] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [perPage, setPerPage] = useState(20)

  const fetchResults = async (page = currentPage, filter = filterTowerJumps, sortBy = sortConfig.key, sortOrder = sortConfig.direction) => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/results`, {
        params: {
          page,
          per_page: perPage,
          filter,
          sort_by: sortBy,
          sort_order: sortOrder
        }
      })
      setResults(response.data.results)
      setPagination(response.data.pagination)
    } catch (error) {
      console.error('Failed to fetch results:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResults()
  }, [currentPage, perPage, filterTowerJumps, sortConfig])

  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage)
  }

  const handleFilterChange = (newFilter) => {
    setFilterTowerJumps(newFilter)
    setCurrentPage(1) // Reset to first page when filtering
  }

  const handlePerPageChange = (newPerPage) => {
    setPerPage(newPerPage)
    setCurrentPage(1) // Reset to first page when changing page size
  }

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <ChevronUp className="h-4 w-4 text-gray-400" />
    }
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="h-4 w-4 text-gray-600" />
    ) : (
      <ChevronDown className="h-4 w-4 text-gray-600" />
    )
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <span className="ml-3 text-gray-600">Loading results...</span>
        </div>
      </div>
    )
  }

  const formatDateTime = (dateStr) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatDuration = (minutes) => {
    if (minutes < 60) {
      return `${Math.round(minutes)}m`
    }
    const hours = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    return `${hours}h ${mins}m`
  }

  return (
    <div className="p-6">
      <div className="flex flex-col sm:flex-row justify-between items-center mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4 sm:mb-0">
          Analysis Results ({pagination?.total_count || 0} total)
        </h3>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Show:</label>
            <select
              value={perPage}
              onChange={(e) => handlePerPageChange(parseInt(e.target.value))}
              className="px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Filter:</label>
            <select
              value={filterTowerJumps}
              onChange={(e) => handleFilterChange(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Periods</option>
              <option value="jumps">Tower Jumps Only</option>
              <option value="normal">Normal Movement</option>
            </select>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                <button
                  onClick={() => handleSort('TimeStart')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Time Period</span>
                  {getSortIcon('TimeStart')}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                State
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                <button
                  onClick={() => handleSort('DurationMinutes')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Duration</span>
                  {getSortIcon('DurationMinutes')}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                Tower Jump
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                <button
                  onClick={() => handleSort('ConfidenceLevel')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Confidence</span>
                  {getSortIcon('ConfidenceLevel')}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                <button
                  onClick={() => handleSort('MaxSpeedKMH')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Max Speed</span>
                  {getSortIcon('MaxSpeedKMH')}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                Changes
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {results.map((result, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div className="font-medium">{formatDateTime(result.TimeStart)}</div>
                    <div className="text-gray-500">{formatDateTime(result.TimeEnd)}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div className="font-medium">{result.State}</div>
                    {result.StateChanges > 0 && (
                      <div className="text-xs text-gray-500 truncate max-w-24" title={result.AllStates}>
                        {result.AllStates}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDuration(result.DurationMinutes)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {result.IsTowerJump === "yes" ? (
                      <div className="flex items-center text-red-600">
                        <AlertTriangle className="h-4 w-4 mr-1" />
                        <span className="text-sm font-medium">Yes</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        <span className="text-sm font-medium">No</span>
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <ConfidenceIndicator confidence={result.ConfidenceLevel} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span className={result.MaxSpeedKMH > 1000 ? 'text-red-600 font-medium' : ''}>
                    {result.MaxSpeedKMH} km/h
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div>{result.StateChanges} state changes</div>
                    <div className="text-xs text-gray-500">{result.RecordCount} records</div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {pagination && pagination.total_pages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((pagination.current_page - 1) * pagination.per_page) + 1} to {Math.min(pagination.current_page * pagination.per_page, pagination.total_count)} of {pagination.total_count} results
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handlePageChange(pagination.current_page - 1)}
                disabled={!pagination.has_prev}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </button>

              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  let pageNum;
                  if (pagination.total_pages <= 5) {
                    pageNum = i + 1;
                  } else if (pagination.current_page <= 3) {
                    pageNum = i + 1;
                  } else if (pagination.current_page >= pagination.total_pages - 2) {
                    pageNum = pagination.total_pages - 4 + i;
                  } else {
                    pageNum = pagination.current_page - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`px-3 py-2 text-sm font-medium rounded-md ${
                        pageNum === pagination.current_page
                          ? 'bg-indigo-600 text-white'
                          : 'text-gray-700 hover:bg-gray-50 border border-gray-300'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={() => handlePageChange(pagination.current_page + 1)}
                disabled={!pagination.has_next}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </button>
            </div>
          </div>
        </div>
      )}

      {results.length === 0 && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500">No results match the current filter.</p>
        </div>
      )}
    </div>
  )
}