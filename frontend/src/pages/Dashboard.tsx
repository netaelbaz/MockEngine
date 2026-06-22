import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Pagination } from '../components/Pagination'
import { MethodBadge } from '../components/MethodBadge'
import { analyticsApi } from '../lib/api'
import type { TimeRange, AnalyticsOverview, InterceptionAnalytics, ErrorDistributionItem, LatencyByHourItem } from '../types'
import {
  PieChart, Pie, Cell, Tooltip as ReTooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from 'recharts'

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState<TimeRange>('today')
  const [mode, setMode] = useState<'general' | 'interception'>('general')

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

function LatencyByHourChart({ data }: { data: LatencyByHourItem[] }) {
  if (data.length === 0) {
    return (
      <Card>
        <h2 className="text-xl font-semibold mb-4">Average Latency by Hour</h2>
        <p className="text-center text-zinc-400 py-8">No latency data in this time range.</p>
      </Card>
    )
  }

  const chartData = data.map(d => ({ hour: hourLabel(d.hour), avg_ms: d.avg_ms }))

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-4">Average Latency by Hour</h2>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 4, right: 24, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
          <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
          <YAxis unit="ms" tick={{ fontSize: 12 }} />
          <ReTooltip formatter={(value: number) => [`${value} ms`, 'Avg latency']} />
          <Line type="monotone" dataKey="avg_ms" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}

const DASH_PAGE_SIZE = 3

function GeneralMode({ overview }: { overview: AnalyticsOverview }) {
  const [versionsPage, setVersionsPage] = useState(0)
  const [endpointsPage, setEndpointsPage] = useState(0)

  const paginatedVersions = overview.app_versions.slice(versionsPage * DASH_PAGE_SIZE, (versionsPage + 1) * DASH_PAGE_SIZE)
  const paginatedEndpoints = overview.endpoints.slice(endpointsPage * DASH_PAGE_SIZE, (endpointsPage + 1) * DASH_PAGE_SIZE)

  return (
    <div>
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Active Rules" value={overview.calls.unique_endpoints.toString()} />
        <StatCard label="Connected Devices" value={overview.devices.total_connected.toString()} />
        <StatCard label="Total Calls" value={overview.calls.total_calls.toString()} />
        <StatCard
          label="Latest Version"
          value={overview.app_versions[0]?.version || 'N/A'}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <ErrorDistributionChart data={overview.error_distribution} />
        <LatencyByHourChart data={overview.latency_by_hour} />
      </div>

      {/* App Version Distribution */}
      <Card className="mb-6">
        <h2 className="text-xl font-semibold mb-4">App Version Distribution</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">App Version</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Connected Devices</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Percentage</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {overview.app_versions.length === 0 ? (
              <tr><td colSpan={4} className="py-8 text-center text-zinc-400">No devices connected yet — install the Android SDK to start collecting data.</td></tr>
            ) : paginatedVersions.map((version) => (
              <tr key={version.version} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{version.version}</td>
                <td className="py-4 px-4">{version.count}</td>
                <td className="py-4 px-4">{version.percentage}%</td>
                <td className="py-4 px-4">
                  {version.is_latest ? (
                    <span className="text-green-600 font-semibold">Latest</span>
                  ) : (
                    <span className="text-zinc-500">Older version</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination total={overview.app_versions.length} pageSize={DASH_PAGE_SIZE} page={versionsPage} onPageChange={setVersionsPage} />
      </Card>

      {/* Endpoint Analytics */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Endpoint Analytics</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Endpoint</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Method</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Calls</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Avg Response</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Intercepted</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">WiFi/Cellular</th>
            </tr>
          </thead>
          <tbody>
            {overview.endpoints.length === 0 ? (
              <tr><td colSpan={6} className="py-8 text-center text-zinc-400">No API calls logged yet — calls will appear here once devices start sending traffic.</td></tr>
            ) : paginatedEndpoints.map((endpoint) => (
              <tr key={endpoint.endpoint + endpoint.method} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{endpoint.endpoint}</td>
                <td className="py-4 px-4">
                  <MethodBadge method={endpoint.method} />
                </td>
                <td className="py-4 px-4">{endpoint.call_count}</td>
                <td className="py-4 px-4">
                  {endpoint.avg_response_time_ms ? `${endpoint.avg_response_time_ms} ms` : 'N/A'}
                </td>
                <td className="py-4 px-4">{endpoint.was_intercepted_count}</td>
                <td className="py-4 px-4">
                  {endpoint.wifi_calls} / {endpoint.cellular_calls}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination total={overview.endpoints.length} pageSize={DASH_PAGE_SIZE} page={endpointsPage} onPageChange={setEndpointsPage} />
      </Card>
    </div>
  )
}

function InterceptionMode({ interceptions }: { interceptions: InterceptionAnalytics }) {
  const [mostInterceptedPage, setMostInterceptedPage] = useState(0)
  const [recentPage, setRecentPage] = useState(0)

  const paginatedMostIntercepted = interceptions.most_intercepted_endpoints.slice(mostInterceptedPage * DASH_PAGE_SIZE, (mostInterceptedPage + 1) * DASH_PAGE_SIZE)
  const paginatedRecent = interceptions.recent_interceptions.slice(recentPage * DASH_PAGE_SIZE, (recentPage + 1) * DASH_PAGE_SIZE)

  return (
    <div>
      <div className="grid grid-cols-2 gap-4 mb-6">
        <StatCard label="Total Interceptions" value={interceptions.total_interceptions.toString()} />
        <StatCard
          label="Most Intercepted"
          value={interceptions.most_intercepted_endpoints[0]?.endpoint || 'N/A'}
        />
      </div>

      {/* Most Intercepted Endpoints */}
      <Card className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Most Intercepted Endpoints</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Endpoint</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Count</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Rule Name</th>
            </tr>
          </thead>
          <tbody>
            {interceptions.most_intercepted_endpoints.length === 0 ? (
              <tr><td colSpan={3} className="py-8 text-center text-zinc-400">No interceptions recorded yet in this time range.</td></tr>
            ) : paginatedMostIntercepted.map((item) => (
              <tr key={item.endpoint} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{item.endpoint}</td>
                <td className="py-4 px-4">{item.count}</td>
                <td className="py-4 px-4">{item.rule_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination total={interceptions.most_intercepted_endpoints.length} pageSize={DASH_PAGE_SIZE} page={mostInterceptedPage} onPageChange={setMostInterceptedPage} />
      </Card>

      {/* Recent Interceptions */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Recent Interceptions</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Endpoint</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Rule</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Device</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {interceptions.recent_interceptions.length === 0 ? (
              <tr><td colSpan={4} className="py-8 text-center text-zinc-400">No recent interceptions in this time range.</td></tr>
            ) : paginatedRecent.map((item) => (
              <tr key={item.id} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{item.endpoint}</td>
                <td className="py-4 px-4">{item.rule_name}</td>
                <td className="py-4 px-4">{item.device_id}</td>
                <td className="py-4 px-4 text-sm text-zinc-500">
                  {new Date(item.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination total={interceptions.recent_interceptions.length} pageSize={DASH_PAGE_SIZE} page={recentPage} onPageChange={setRecentPage} />
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
