import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Pagination } from '../components/Pagination'
import { MethodBadge } from '../components/MethodBadge'
import { analyticsApi } from '../lib/api'
import type { TimeRange, AnalyticsOverview, InterceptionAnalytics, ErrorDistributionItem, TrafficOverTimeItem, RuleEffectiveness, EndpointInterceptionRate, DeviceHealth, AppVersionStat} from '../types'
import {
  PieChart, Pie, Cell, Tooltip as ReTooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from 'recharts'

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState<TimeRange>('today')
  const [searchParams, setSearchParams] = useSearchParams()
  const rawMode = searchParams.get('mode')
  const mode: 'general' | 'interception' = rawMode === 'interception' ? 'interception' : 'general'
  const setMode = (m: 'general' | 'interception') => setSearchParams({ mode: m }, { replace: true })

  // Fetch analytics overview
  const { data: overview, isLoading: overviewLoading, isError: overviewError } = useQuery({
    queryKey: ['analytics', 'overview', timeRange],
    queryFn: () => analyticsApi.getOverview(timeRange),
    refetchInterval: 30000,
  })

  // Fetch interception analytics
  const { data: interceptions, isLoading: interceptionsLoading, isError: interceptionsError } = useQuery({
    queryKey: ['analytics', 'interceptions', timeRange],
    queryFn: () => analyticsApi.getInterceptions(timeRange),
    refetchInterval: 30000,
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-7">
        <div>
          <div className="text-zinc-500 text-sm mb-1.5">Dashboard</div>
          <h1 className="text-3xl mb-2">SDK Overview</h1>
          <p className="text-zinc-600 text-base">
            Monitor rules, connected devices, interceptions and app version usage.
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
            className="px-4 py-3 rounded-xl border border-zinc-300 text-base bg-white"
          >
            <option value="today">Today</option>
            <option value="week">Past Week</option>
            <option value="month">Past Month</option>
          </select>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode('general')}
          className={`px-6 py-3 rounded-xl text-base font-medium transition-colors ${
            mode === 'general'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-zinc-700 border border-zinc-300'
          }`}
        >
          General
        </button>
        <button
          onClick={() => setMode('interception')}
          className={`px-6 py-3 rounded-xl text-base font-medium transition-colors ${
            mode === 'interception'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-zinc-700 border border-zinc-300'
          }`}
        >
          Interception
        </button>
      </div>

      {(() => {
        if (mode === 'general') {
          if (overviewLoading) return <div className="text-center py-12 text-zinc-500">Loading...</div>
          if (overviewError) return <ErrorBanner message="Failed to load dashboard data. Is the backend running?" />
          if (!overview) return null
          return <GeneralMode overview={overview} />
        }
        if (mode === 'interception') {
          if (interceptionsLoading) return <div className="text-center py-12 text-zinc-500">Loading...</div>
          if (interceptionsError) return <ErrorBanner message="Failed to load interception data. Is the backend running?" />
          if (!interceptions) return null
          return <InterceptionMode interceptions={interceptions} />
        }
        return null
      })()}
    </div>
  )
}

const ERROR_COLORS: Record<string, string> = {
  '2': '#22c55e',
  '3': '#3b82f6',
  '4': '#f97316',
  '5': '#ef4444',
}

function errorColor(statusCode: number): string {
  return ERROR_COLORS[String(statusCode)[0]] ?? '#a1a1aa'
}

function hourLabel(hour: string): string {
  const h = parseInt(hour, 10)
  if (h === 0) return '12AM'
  if (h < 12) return `${h}AM`
  if (h === 12) return '12PM'
  return `${h - 12}PM`
}

function ErrorDistributionChart({ data }: { data: ErrorDistributionItem[] }) {
  if (data.length === 0) {
    return (
      <Card>
        <h2 className="text-xl font-semibold mb-4">Error Distribution</h2>
        <p className="text-center text-zinc-400 py-8">No errors recorded in this time range.</p>
      </Card>
    )
  }

  const chartData = data.map(d => ({
    name: String(d.status_code),
    value: d.count,
    color: errorColor(d.status_code),
  }))

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-4">Error Distribution</h2>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <ReTooltip formatter={(value: number, name: string) => [value, `HTTP ${name}`]} />
          <Legend formatter={(value) => `HTTP ${value}`} />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}

function TrafficOverTimeChart({ data, timeRange }: { data: TrafficOverTimeItem[]; timeRange: TimeRange }) {
  if (data.length === 0) {
    return (
      <Card>
        <h2 className="text-xl font-semibold mb-4">Requests Activity</h2>
        <p className="text-center text-zinc-400 py-8">No traffic data in this time range.</p>
      </Card>
    )
  }

  function formatBucket(bucket: string): string {
    if (timeRange === 'today') return hourLabel(bucket)
    const [, month, day] = bucket.split('-')
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return `${months[parseInt(month, 10) - 1]} ${parseInt(day, 10)}`
  }

  const chartData = data.map(d => ({
    label: formatBucket(d.bucket),
    total: d.total,
    intercepted: d.intercepted,
  }))

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-4">Requests Activity</h2>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <ReTooltip
            formatter={(value, name) => [
              value ?? 0,
              name === 'total' ? 'Total Requests' : 'Intercepted Requests',
            ]}
          />
          <Legend formatter={(value) => value === 'total' ? 'Total Requests' : 'Intercepted'} />
          <Line type="monotone" dataKey="total" name="total" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
          <Line type="monotone" dataKey="intercepted" name="intercepted" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}

function AppVersionAdoptionChart({ versions }: { versions: AppVersionStat[] }) {
  const barColors = ['#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#d4d4d8']

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-5">App Version Distribution</h2>
      {versions.length === 0 ? (
        <p className="text-zinc-400 text-sm text-center py-6">No devices connected yet — install the Android SDK to start collecting data.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {versions.map((v, i) => (
            <div key={v.version} className="flex items-center gap-3">
              <span className="text-sm font-mono w-16 text-right text-zinc-700 shrink-0">{v.version}</span>
              <div className="flex-1 bg-zinc-100 rounded-full h-5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${v.percentage}%`, backgroundColor: barColors[Math.min(i, barColors.length - 1)] }}
                />
              </div>
              <span className="text-sm font-semibold text-zinc-700 w-10 text-right shrink-0">{v.percentage}%</span>
              {v.is_latest && (
                <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full shrink-0">latest</span>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}


const DASH_PAGE_SIZE = 3

function DeviceHealthCard({ health }: { health: DeviceHealth }) {
  return (
    <Card>
      <h2 className="text-base font-semibold mb-3">Device Health</h2>
      <div className="grid grid-cols-2 gap-y-3 gap-x-6">
        <div>
          <div className="text-xs text-zinc-500 mb-0.5">Connected</div>
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 shrink-0" />
            <span className="text-lg font-bold">{health.connected}</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 mb-0.5">Offline Today</div>
          <div className="flex items-center gap-1.5">
            {health.offline_today > 0 && (
              <span className="inline-block w-2 h-2 rounded-full bg-red-400 shrink-0" />
            )}
            <span className="text-lg font-bold">{health.offline_today}</span>
          </div>
        </div>
      </div>
    </Card>
  )
}

function GeneralMode({ overview }: { overview: AnalyticsOverview }) {
  const [endpointsPage, setEndpointsPage] = useState(0)
  const paginatedEndpoints = overview.endpoints.slice(endpointsPage * DASH_PAGE_SIZE, (endpointsPage + 1) * DASH_PAGE_SIZE)

  return (
    <div>
      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <StatCard label="Total Calls" value={overview.calls.total_calls.toString()} />
        <StatCard
          label="Latest Version"
          value={overview.app_versions[0]?.version || 'N/A'}
        />
      </div>

      {/* Main grid: left col = Device Health + Error Distribution, right cols = Traffic + App Versions */}
      <div className="grid grid-cols-3 gap-4 mb-6 items-start">
        {/* Left column */}
        <div className="flex flex-col gap-4">
          {overview.device_health
            ? <DeviceHealthCard health={overview.device_health} />
            : <Card><h2 className="text-base font-semibold mb-3">Device Health</h2><p className="text-zinc-400 text-xs">Restart the backend to enable device health metrics.</p></Card>
          }
          <ErrorDistributionChart data={overview.error_distribution} />
        </div>

        {/* Right columns */}
        <div className="col-span-2 flex flex-col gap-4">
          <TrafficOverTimeChart data={overview.traffic_over_time} timeRange={overview.time_range} />
          <AppVersionAdoptionChart versions={overview.app_versions} />
        </div>
      </div>

      {/* Endpoint Analytics */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Endpoint Analytics</h2>
        <table className="w-full table-fixed">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-2 px-3 text-xs text-zinc-600 font-medium w-2/5">Endpoint</th>
              <th className="text-left py-2 px-3 text-xs text-zinc-600 font-medium w-[10%]">Method</th>
              <th className="text-right py-2 px-3 text-xs text-zinc-600 font-medium w-[10%]">Calls</th>
              <th className="text-right py-2 px-3 text-xs text-zinc-600 font-medium w-[12%]">Avg Response</th>
              <th className="text-right py-2 px-3 text-xs text-zinc-600 font-medium w-[12%]">Intercepted</th>
              <th className="text-left py-2 px-3 text-xs text-zinc-600 font-medium">Network Type</th>
            </tr>
          </thead>
          <tbody>
            {overview.endpoints.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-zinc-400">No API calls logged yet — calls will appear here once devices start sending traffic.</td></tr>
            ) : paginatedEndpoints.map((endpoint) => {
              const netTotal = endpoint.wifi_calls + endpoint.cellular_calls
              const wifiPct = netTotal === 0 ? 0 : Math.round((endpoint.wifi_calls / netTotal) * 100)
              const cellPct = 100 - wifiPct
              return (
                <tr key={endpoint.endpoint + endpoint.method} className="border-b border-zinc-200 hover:bg-neutral-50">
                  <td className="py-3 px-3 text-xs font-mono font-medium truncate">{endpoint.endpoint}</td>
                  <td className="py-3 px-3"><MethodBadge method={endpoint.method} /></td>
                  <td className="py-3 px-3 text-xs text-right">{endpoint.call_count.toLocaleString()}</td>
                  <td className="py-3 px-3 text-xs text-right">{endpoint.avg_response_time_ms ? `${endpoint.avg_response_time_ms} ms` : 'N/A'}</td>
                  <td className="py-3 px-3 text-xs text-right">{endpoint.was_intercepted_count.toLocaleString()}</td>
                  <td className="py-3 px-3">
                    {netTotal === 0 ? (
                      <span className="text-xs text-zinc-400">—</span>
                    ) : (
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden flex">
                          <div className="h-full bg-blue-500" style={{ width: `${wifiPct}%` }} />
                          <div className="h-full bg-orange-400" style={{ width: `${cellPct}%` }} />
                        </div>
                        <span className="text-xs text-zinc-500 shrink-0 w-24 text-right">
                          W {wifiPct}% · C {cellPct}%
                        </span>
                      </div>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        <Pagination total={overview.endpoints.length} pageSize={DASH_PAGE_SIZE} page={endpointsPage} onPageChange={setEndpointsPage} />
      </Card>

    </div>
  )
}

function relativeTime(iso: string | null): string {
  if (!iso) return 'Never'
  const normalized = iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z'
  const diff = Date.now() - new Date(normalized).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (hours < 48) return 'Yesterday'
  return `${Math.floor(hours / 24)} days ago`
}

function formatHits(n: number): string {
  return n.toLocaleString()
}

function RuleEffectivenessCard({ data }: { data: RuleEffectiveness[] }) {
  const [page, setPage] = useState(0)
  const paginated = data.slice(page * DASH_PAGE_SIZE, (page + 1) * DASH_PAGE_SIZE)
  return (
    <Card>
      <h2 className="text-lg font-semibold mb-3">Rule Effectiveness</h2>
      <table className="w-full table-fixed">
        <thead>
          <tr className="border-b border-zinc-200">
            <th className="text-left py-2 px-2 text-xs text-zinc-600 font-medium w-1/2">Rule Name</th>
            <th className="text-right py-2 px-2 text-xs text-zinc-600 font-medium w-1/6">Hits</th>
            <th className="text-left py-2 px-2 text-xs text-zinc-600 font-medium">Last Used</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={3} className="py-8 text-center text-zinc-400">No rules configured yet.</td></tr>
          ) : paginated.map((item) => (
            <tr key={item.rule_id} className="border-b border-zinc-200 hover:bg-neutral-50">
              <td className="py-2 px-2 font-medium text-xs truncate">{item.rule_name}</td>
              <td className="py-2 px-2 text-xs text-right">{formatHits(item.hits)}</td>
              <td className="py-2 px-2 text-xs text-zinc-500">{relativeTime(item.last_used)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination total={data.length} pageSize={DASH_PAGE_SIZE} page={page} onPageChange={setPage} />
    </Card>
  )
}

function EndpointInterceptionRateCard({ data }: { data: EndpointInterceptionRate[] }) {
  const [page, setPage] = useState(0)
  const paginated = data.slice(page * DASH_PAGE_SIZE, (page + 1) * DASH_PAGE_SIZE)
  return (
    <Card>
      <h2 className="text-lg font-semibold mb-3">Endpoint Interception Rate</h2>
      <table className="w-full table-fixed">
        <thead>
          <tr className="border-b border-zinc-200">
            <th className="text-left py-2 px-2 text-xs text-zinc-600 font-medium w-2/5">Endpoint</th>
            <th className="text-left py-2 px-2 text-xs text-zinc-600 font-medium w-[10%]">Method</th>
            <th className="text-right py-2 px-2 text-xs text-zinc-600 font-medium w-[13%]">Total Calls</th>
            <th className="text-right py-2 px-2 text-xs text-zinc-600 font-medium w-[13%]">Intercepted</th>
            <th className="text-left py-2 px-2 text-xs text-zinc-600 font-medium">Rate</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={5} className="py-8 text-center text-zinc-400">No API calls logged yet in this time range.</td></tr>
          ) : paginated.map((item) => (
            <tr key={item.endpoint + item.method} className="border-b border-zinc-200 hover:bg-neutral-50">
              <td className="py-2 px-2 text-xs font-mono font-medium truncate">{item.endpoint}</td>
              <td className="py-2 px-2"><MethodBadge method={item.method} /></td>
              <td className="py-2 px-2 text-xs text-right">{item.total_calls.toLocaleString()}</td>
              <td className="py-2 px-2 text-xs text-right">{item.intercepted.toLocaleString()}</td>
              <td className="py-2 px-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        item.rate === 0 ? '' :
                        item.rate < 33 ? 'bg-yellow-400' :
                        item.rate < 66 ? 'bg-green-300' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(item.rate, 100)}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-zinc-700 w-10 text-right shrink-0">
                    {item.rate % 1 === 0 ? `${item.rate}%` : `${item.rate.toFixed(1)}%`}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination total={data.length} pageSize={DASH_PAGE_SIZE} page={page} onPageChange={setPage} />
    </Card>
  )
}

function groupInterceptions(items: InterceptionAnalytics['recent_interceptions']) {
  const map = new Map<string, { endpoint: string; rule_name: string; hits: number; last_seen: string }>()
  for (const item of items) {
    const key = `${item.endpoint}||${item.rule_name}`
    const existing = map.get(key)
    const ts = item.timestamp.endsWith('Z') ? item.timestamp : item.timestamp + 'Z'
    if (!existing) {
      map.set(key, { endpoint: item.endpoint, rule_name: item.rule_name, hits: 1, last_seen: ts })
    } else {
      existing.hits += 1
      if (ts > existing.last_seen) existing.last_seen = ts
    }
  }
  return Array.from(map.values()).sort((a, b) => b.last_seen.localeCompare(a.last_seen))
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

function InterceptionMode({ interceptions }: { interceptions: InterceptionAnalytics }) {
  const [recentPage, setRecentPage] = useState(0)

  const grouped = groupInterceptions(interceptions.recent_interceptions)
  const paginatedRecent = grouped.slice(recentPage * DASH_PAGE_SIZE, (recentPage + 1) * DASH_PAGE_SIZE)

  return (
    <div>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Active Rules" value={interceptions.rule_effectiveness.length.toString()} />
        <StatCard label="Total Interceptions" value={interceptions.total_interceptions.toString()} />
        <StatCard
          label="Most Intercepted"
          value={interceptions.most_intercepted_endpoints[0]?.endpoint || 'N/A'}
        />
      </div>

      {/* Analytics cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <RuleEffectivenessCard data={interceptions.rule_effectiveness} />
        <EndpointInterceptionRateCard data={interceptions.endpoint_interception_rate} />
      </div>

      {/* Recent Interceptions */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Recent Interceptions</h2>
        <table className="w-full table-fixed">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-3 px-3 text-xs text-zinc-600 font-medium w-2/5">Endpoint</th>
              <th className="text-left py-3 px-3 text-xs text-zinc-600 font-medium">Rule</th>
              <th className="text-right py-3 px-3 text-xs text-zinc-600 font-medium w-16">Hits</th>
              <th className="text-right py-3 px-3 text-xs text-zinc-600 font-medium w-24">Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {grouped.length === 0 ? (
              <tr><td colSpan={4} className="py-8 text-center text-zinc-400">No recent interceptions in this time range.</td></tr>
            ) : paginatedRecent.map((item) => (
              <tr key={item.endpoint + item.rule_name} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-3 px-3 text-xs font-mono font-medium truncate">{item.endpoint}</td>
                <td className="py-3 px-3 text-xs truncate">{item.rule_name}</td>
                <td className="py-3 px-3 text-xs text-right font-semibold">{item.hits}</td>
                <td className="py-3 px-3 text-xs text-right text-zinc-500">{formatTime(item.last_seen)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination total={grouped.length} pageSize={DASH_PAGE_SIZE} page={recentPage} onPageChange={setRecentPage} />
      </Card>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-zinc-200">
      <div className="text-zinc-500 text-sm mb-2">{label}</div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  )
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-2xl p-6 shadow-sm border border-zinc-200 ${className}`}>
      {children}
    </div>
  )
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 px-6 py-5 text-red-700">
      <div className="font-semibold mb-1">Could not load data</div>
      <div className="text-sm">{message}</div>
    </div>
  )
}
