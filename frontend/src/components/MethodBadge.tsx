const METHOD_COLORS: Record<string, string> = {
  GET:    'bg-blue-100 text-blue-700',
  POST:   'bg-green-100 text-green-700',
  PUT:    'bg-orange-100 text-orange-700',
  DELETE: 'bg-red-100 text-red-600',
  PATCH:  'bg-teal-100 text-teal-700',
  ANY:    'bg-gray-100 text-gray-600',
}

export function MethodBadge({ method }: { method: string }) {
  const color = METHOD_COLORS[method?.toUpperCase()] ?? 'bg-gray-400 text-white'
  return (
    <span className={`px-3 py-1 rounded-md text-xs font-bold tracking-wide ${color}`}>
      {method || 'GET'}
    </span>
  )
}
