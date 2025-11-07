export default function ConfidenceIndicator({ confidence }) {
  const getConfidenceColor = (conf) => {
    if (conf >= 80) return 'from-emerald-500 to-emerald-600'
    if (conf >= 60) return 'from-amber-500 to-amber-600'
    if (conf >= 40) return 'from-orange-500 to-orange-600'
    return 'from-red-500 to-red-600'
  }

  const getConfidenceTextColor = (conf) => {
    if (conf >= 80) return 'text-emerald-700'
    if (conf >= 60) return 'text-amber-700'
    if (conf >= 40) return 'text-orange-700'
    return 'text-red-700'
  }

  const getConfidenceBgColor = (conf) => {
    if (conf >= 80) return 'bg-emerald-50'
    if (conf >= 60) return 'bg-amber-50'
    if (conf >= 40) return 'bg-orange-50'
    return 'bg-red-50'
  }

  return (
    <div className="flex items-center space-x-3">
      <div className="w-20 bg-slate-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-2 rounded-full bg-gradient-to-r transition-all duration-500 ${getConfidenceColor(confidence)}`}
          style={{ width: `${confidence}%` }}
        ></div>
      </div>
      <span
        className={`text-xs font-semibold px-2.5 py-1 rounded-lg ${getConfidenceTextColor(
          confidence
        )} ${getConfidenceBgColor(confidence)}`}
      >
        {confidence}%
      </span>
    </div>
  )
}