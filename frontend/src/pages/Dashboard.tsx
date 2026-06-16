import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../lib/api'
import type { TimeRange, AnalyticsOverview, InterceptionAnalytics } from '../types'

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState<TimeRange>('today')
  const [mode, setMode] = useState<'general' | 'interception'>('general')

  // Fetch analytics overview
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['analytics', 'overview', timeRange],
    queryFn: () => analyticsApi.getOverview(timeRange),
    refetchInterval: 30000, // 30 seconds
  })

  // Fetch interception analytics
  const { data: interceptions, isLoading: interceptionsLoading } = useQuery({
    queryKey: ['analytics', 'interceptions', timeRange],
    queryFn: () => analyticsApi.getInterceptions(timeRange),
    refetchInterval: 30000, // 30 seconds
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

      {overviewLoading ? (
        <div className="text-center py-12 text-zinc-500">Loading...</div>
      ) : mode === 'general' && overview ? (
        <GeneralMode overview={overview} />
      ) : interceptions ? (
        <InterceptionMode interceptions={interceptions} />
      ) : null}
    </div>
  )
}

function GeneralMode({ overview }: { overview: AnalyticsOverview }) {
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
            {overview.app_versions.map((version) => (
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
            {overview.endpoints.map((endpoint) => (
              <tr key={endpoint.endpoint + endpoint.method} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{endpoint.endpoint}</td>
                <td className="py-4 px-4">
                  <span className="px-3 py-1 rounded-full border border-zinc-300 text-xs font-semibold">
                    {endpoint.method}
                  </span>
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
      </Card>
    </div>
  )
}

function InterceptionMode({ interceptions }: { interceptions: InterceptionAnalytics }) {
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
            {interceptions.most_intercepted_endpoints.map((item) => (
              <tr key={item.endpoint} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{item.endpoint}</td>
                <td className="py-4 px-4">{item.count}</td>
                <td className="py-4 px-4">{item.rule_name}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
            {interceptions.recent_interceptions.map((item) => (
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
