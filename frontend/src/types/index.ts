// ==================== API Key Types ====================

export interface ApiKey {
  id: number
  name: string
  api_key: string
  is_active: boolean
  created_at: string
}

export interface ApiKeyCreate {
  key_name: string
}

// ==================== Rule Types ====================

export interface Rule {
  id: number
  name: string
  url_pattern: string
  method: string
  status_code: number
  delay_s: number
  mock_data: Record<string, unknown>
  ai_prompt?: string
  is_enabled: boolean
  created_at: string
  updated_at: string
  created_by_key_id?: number
}

export interface RuleCreate {
  name: string
  url_pattern: string
  method: string
  status_code: number
  delay_s: number
  mock_data: Record<string, unknown>
  ai_prompt?: string
}

export interface RuleUpdate {
  name?: string
  url_pattern?: string
  method?: string
  status_code?: number
  delay_s?: number
  mock_data?: Record<string, unknown>
  is_enabled?: boolean
  ai_prompt?: string
}

export interface AIGenerateRequest {
  prompt: string
  url_pattern?: string
  method?: string
}

export interface AIGenerateResponse {
  mock_data: Record<string, unknown>
}

// ==================== Device Types ====================

export type InternetMode = 'wifi' | 'cellular' | 'none'

export interface Device {
  id: number
  device_id: string
  api_key_id: number
  app_version: string
  android_version?: string
  internet_mode: InternetMode
  first_seen: string
  last_seen: string
}

// ==================== Analytics Types ====================

export type TimeRange = 'today' | 'week' | 'month'

export interface AndroidVersionStat {
  version: string
  count: number
}

export interface DeviceStats {
  total_connected: number
  active_today: number
  android_versions: AndroidVersionStat[]
  internet_modes: Record<string, number>
}

export interface CallStats {
  total_calls: number
  unique_endpoints: number
  intercepted_count: number
  interception_rate: number
}

export interface EndpointAnalytics {
  endpoint: string
  method: string
  call_count: number
  avg_response_time_ms: number | null
  was_intercepted_count: number
  wifi_calls: number
  cellular_calls: number
}

export interface AppVersionStat {
  version: string
  count: number
  percentage: number
  is_latest: boolean
}

export interface RecentInterception {
  id: number
  endpoint: string
  rule_name: string
  timestamp: string
  device_id: string
}

export interface ErrorDistributionItem {
  status_code: number
  count: number
}

export interface LatencyByHourItem {
  hour: string
  avg_ms: number
}

export interface AnalyticsOverview {
  time_range: TimeRange
  devices: DeviceStats
  calls: CallStats
  endpoints: EndpointAnalytics[]
  recent_interceptions: RecentInterception[]
  app_versions: AppVersionStat[]
  error_distribution: ErrorDistributionItem[]
  latency_by_hour: LatencyByHourItem[]
}

export interface MostInterceptedEndpoint {
  endpoint: string
  count: number
  rule_name: string
}

export interface RecentInterceptionDetail {
  id: number
  endpoint: string
  rule_name: string
  timestamp: string
  device_id: string
  response_mock_data: Record<string, unknown>
}

export interface RuleUsage {
  rule_id: number
  rule_name: string
  usage_count: number
}

export interface InterceptionAnalytics {
  time_range: TimeRange
  total_interceptions: number
  most_intercepted_endpoints: MostInterceptedEndpoint[]
  recent_interceptions: RecentInterceptionDetail[]
  rule_usage: RuleUsage[]
}

export interface DeviceAnalytics {
  total_devices: number
  active_today: number
  devices_by_version: AppVersionStat[]
  devices_by_android_version: AndroidVersionStat[]
  recent_devices: Device[]
}

// ==================== Common Types ====================

export interface SuccessResponse {
  status: string
  message: string
}
