import { useState, useRef } from 'react'
import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { rulesApi, aiApi } from '../lib/api'
import type { Rule, RuleCreate, RuleUpdate } from '../types'
import { Pagination } from '../components/Pagination'
import { MethodBadge } from '../components/MethodBadge'
import { Sparkles } from 'lucide-react'

function extractApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail ?? 'Something went wrong. Please try again.'
  }
  return 'Something went wrong. Please try again.'
}

const PAGE_SIZE = 8

export default function Rules() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [expandedRuleId, setExpandedRuleId] = useState<string | null>(null)
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [createError, setCreateError] = useState<string | null>(null)
  const [updateError, setUpdateError] = useState<string | null>(null)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: () => rulesApi.list(),
    refetchInterval: 180000,
  })

  const createMutation = useMutation({
    mutationFn: (rule: RuleCreate) => rulesApi.create(rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
      setShowCreateForm(false)
      setCreateError(null)
    },
    onError: (error: unknown) => {
      setCreateError(extractApiError(error))
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ ruleId, data }: { ruleId: string; data: RuleUpdate }) =>
      rulesApi.update(ruleId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
      setEditingRuleId(null)
      setUpdateError(null)
    },
    onError: (error: unknown) => {
      setUpdateError(extractApiError(error))
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (ruleId: string) => rulesApi.delete(ruleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: ({ ruleId, isEnabled }: { ruleId: string; isEnabled: boolean }) =>
      rulesApi.update(ruleId, { is_enabled: !isEnabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
    },
  })

  const filteredRules = rules?.filter((rule) =>
    rule.name.toLowerCase().includes(search.toLowerCase()) ||
    rule.url_pattern.toLowerCase().includes(search.toLowerCase())
  ) || []

  const paginatedRules = filteredRules.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const handleRowClick = (ruleId: string) => {
    if (expandedRuleId === ruleId) {
      setExpandedRuleId(null)
      setEditingRuleId(null)
    } else {
      setExpandedRuleId(ruleId)
      setEditingRuleId(null)
    }
  }

  const handleEditClick = (e: React.MouseEvent, ruleId: string) => {
    e.stopPropagation()
    setExpandedRuleId(ruleId)
    setEditingRuleId(ruleId)
    setUpdateError(null)
  }

  if (isLoading) {
    return <div className="text-center py-12 text-zinc-500">Loading...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-7">
        <div>
          <div className="text-zinc-500 text-sm mb-1.5">Rules</div>
          <h1 className="text-3xl mb-2">Interception Rules</h1>
          <p className="text-zinc-600 text-base">
            Create and manage server behavior rules used by the SDK.
          </p>
        </div>
        <button
          onClick={() => { setShowCreateForm(!showCreateForm); setCreateError(null) }}
          className="px-5 py-3 rounded-xl bg-slate-900 text-white font-semibold"
        >
          {showCreateForm ? 'Cancel' : 'New Rule'}
        </button>
      </div>

      {showCreateForm && (
        <CreateRuleForm
          onSubmit={(rule) => createMutation.mutate(rule)}
          submitError={createError}
        />
      )}

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200">
        <div className="flex justify-between items-center mb-5">
          <input
            type="text"
            placeholder="Search rules by endpoint, name "
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0) }}
            className="w-80 px-4 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Rule</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Method</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Endpoint</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Status</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Delay</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Enabled</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {paginatedRules.map((rule) => {
              const ruleId = rule.id.toString()
              const isExpanded = expandedRuleId === ruleId
              const isEditing = editingRuleId === ruleId

              return (
                <React.Fragment key={rule.id}>
                  <tr
                    className="border-b border-zinc-200 hover:bg-neutral-50 cursor-pointer"
                    onClick={() => handleRowClick(ruleId)}
                  >
                    <td className="py-4 px-4 font-medium">{rule.name}</td>
                    <td className="py-4 px-4">
                      <MethodBadge method={rule.method || 'GET'} />
                    </td>
                    <td className="py-4 px-4">
                      <span className="inline-block bg-blue-50 text-blue-900 text-sm font-mono px-3 py-1 rounded-full">
                        {rule.url_pattern}
                      </span>
                    </td>
                    <td className="py-4 px-4">{rule.status_code ?? '—'}</td>
                    <td className="py-4 px-4">{rule.delay_s} s</td>
                    <td className="py-4 px-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleMutation.mutate({ ruleId, isEnabled: rule.is_enabled })
                        }}
                        className={`w-11 h-6 rounded-full relative transition-colors ${
                          rule.is_enabled ? 'bg-green-500' : 'bg-zinc-300'
                        }`}
                      >
                        <span
                          className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                            rule.is_enabled ? 'right-0.5' : 'left-0.5'
                          }`}
                        />
                      </button>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={(e) => handleEditClick(e, ruleId)}
                          className="text-blue-500 hover:text-blue-700 transition-colors"
                          title="Edit"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            deleteMutation.mutate(ruleId)
                          }}
                          className="text-red-500 hover:text-red-700 transition-colors"
                          title="Delete"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>

                  {isExpanded && (
                    <tr className="bg-neutral-50">
                      <td colSpan={7} className="px-6 py-6">
                        {isEditing ? (
                          <EditRuleForm
                            rule={rule}
                            onSubmit={(data) => updateMutation.mutate({ ruleId, data })}
                            onCancel={() => { setEditingRuleId(null); setUpdateError(null) }}
                            isSaving={updateMutation.isPending}
                            submitError={updateError}
                          />
                        ) : (
                          <ViewRuleDetail rule={rule} />
                        )}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
        <Pagination total={filteredRules.length} pageSize={PAGE_SIZE} page={page} onPageChange={setPage} />
      </div>
    </div>
  )
}

function computeUseMockBackend(statusCode: number | undefined, mockDataJson: string): boolean {
  if (statusCode != null && statusCode >= 400) return true
  try {
    const parsed = JSON.parse(mockDataJson)
    if (Object.keys(parsed).length > 0) return true
  } catch {}
  return false
}

// ── Backend mode selector ─────────────────────────────────────────────────────

function BackendModeSelector({ value, onChange }: { value: boolean; onChange: (v: boolean) => void }) {
  return (
    <div className="col-span-3 flex flex-col gap-1.5">
      <label className="text-sm font-semibold text-zinc-600">Backend Mode</label>
      <div className="grid grid-cols-2 gap-2 p-1 bg-zinc-100 rounded-xl">
        <button
          type="button"
          onClick={() => onChange(true)}
          className={`flex items-start gap-3 px-4 py-3 rounded-lg text-left transition-all ${
            value
              ? 'bg-white shadow-sm ring-1 ring-violet-200'
              : 'hover:bg-zinc-50'
          }`}
        >
          <span className={`mt-0.5 flex-shrink-0 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
            value ? 'border-violet-500' : 'border-zinc-300'
          }`}>
            {value && <span className="w-2 h-2 rounded-full bg-violet-500" />}
          </span>
          <span className="flex flex-col gap-0.5">
            <span className={`text-sm font-semibold ${value ? 'text-violet-700' : 'text-zinc-500'}`}>Mock Backend</span>
            <span className="text-xs text-zinc-400 leading-snug">SDK returns mock response — real server is not called</span>
          </span>
        </button>

        <button
          type="button"
          onClick={() => onChange(false)}
          className={`flex items-start gap-3 px-4 py-3 rounded-lg text-left transition-all ${
            !value
              ? 'bg-white shadow-sm ring-1 ring-green-200'
              : 'hover:bg-zinc-50'
          }`}
        >
          <span className={`mt-0.5 flex-shrink-0 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
            !value ? 'border-green-500' : 'border-zinc-300'
          }`}>
            {!value && <span className="w-2 h-2 rounded-full bg-green-500" />}
          </span>
          <span className="flex flex-col gap-0.5">
            <span className={`text-sm font-semibold ${!value ? 'text-green-700' : 'text-zinc-500'}`}>Call Real Backend</span>
            <span className="text-xs text-zinc-400 leading-snug">SDK hits real server — rule still applies</span>
          </span>
        </button>
      </div>
    </div>
  )
}

// ── View (read-only) ──────────────────────────────────────────────────────────

function ViewRuleDetail({ rule }: { rule: Rule }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-3 gap-4">
        <Field label="Rule Name" value={rule.name} />
        <Field label="Endpoint Pattern" value={rule.url_pattern} className="col-span-2" />
        <Field label="Method" value={rule.method || 'GET'} />
        <Field label="Status Code" value={rule.status_code != null ? String(rule.status_code) : '—'} />
        <Field label="Delay (s)" value={String(rule.delay_s)} />
      </div>
      <div>
        <p className="text-sm font-semibold text-zinc-600 mb-2">Response Body (JSON)</p>
        <pre className="bg-zinc-800 text-zinc-100 p-4 rounded-lg text-sm overflow-x-auto max-h-[300px] overflow-y-auto">
          {JSON.stringify(rule.mock_data, null, 2)}
        </pre>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wide">Backend Mode</span>
        {rule.use_mock_backend ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-violet-100 text-violet-700">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-500" />
            Mock Backend
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
            Call Real Backend
          </span>
        )}
      </div>
    </div>
  )
}

function Field({ label, value, className = '' }: { label: string; value: string; className?: string }) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wide">{label}</span>
      <span className="px-3 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm text-zinc-800">{value}</span>
    </div>
  )
}

// ── Edit form ─────────────────────────────────────────────────────────────────

function EditRuleForm({
  rule,
  onSubmit,
  onCancel,
  isSaving,
  submitError,
}: {
  rule: Rule
  onSubmit: (data: RuleUpdate) => void
  onCancel: () => void
  isSaving: boolean
  submitError?: string | null
}) {
  const [formData, setFormData] = useState<RuleUpdate>({
    name: rule.name,
    url_pattern: rule.url_pattern,
    method: rule.method,
    status_code: rule.status_code,
    delay_s: rule.delay_s,
    mock_data: rule.mock_data,
    use_mock_backend: rule.use_mock_backend,
    ai_prompt: rule.ai_prompt ?? undefined,
  })
  const [mockDataJson, setMockDataJson] = useState(JSON.stringify(rule.mock_data, null, 2))
  const [jsonError, setJsonError] = useState<string | null>(null)
  const [aiPrompt, setAiPrompt] = useState(rule.ai_prompt ?? '')
  const [isGenerating, setIsGenerating] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const text = ev.target?.result as string
      handleJsonChange(text)
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (jsonError) return
    try {
      const parsed = JSON.parse(mockDataJson)
      onSubmit({ ...formData, mock_data: parsed, ai_prompt: aiPrompt || undefined })
    } catch {
      setJsonError('Invalid JSON format')
    }
  }

  const handleJsonChange = (value: string) => {
    setMockDataJson(value)
    try {
      JSON.parse(value)
      setJsonError(null)
    } catch {
      setJsonError('Invalid JSON format')
    }
  }

  const handleGenerate = async () => {
    if (!aiPrompt.trim()) return
    setIsGenerating(true)
    setAiError(null)
    try {
      const result = await aiApi.generateMockData(aiPrompt, formData.url_pattern, formData.method)
      const pretty = JSON.stringify(result.mock_data, null, 2)
      setMockDataJson(pretty)
      setJsonError(null)
    } catch {
      setAiError('Failed to generate data. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div>
      <h3 className="text-base font-semibold mb-4 text-zinc-800">Edit Rule</h3>
      <form onSubmit={handleSubmit} className="grid grid-cols-3 gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Rule Name <span className="text-red-500">*</span></label>
          <input
            type="text"
            required
            value={formData.name ?? ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          />
        </div>

        <div className="col-span-2 flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Endpoint Pattern <span className="text-red-500">*</span></label>
          <input
            type="text"
            required
            value={formData.url_pattern ?? ''}
            onChange={(e) => setFormData({ ...formData, url_pattern: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Method</label>
          <select
            value={formData.method ?? 'GET'}
            onChange={(e) => setFormData({ ...formData, method: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          >
            {['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'ANY'].map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Status Code</label>
          <input
            type="number"
            min="100"
            max="599"
            placeholder="None"
            value={formData.status_code ?? ''}
            onChange={(e) => setFormData({ ...formData, status_code: e.target.value === '' ? null : parseInt(e.target.value) })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Delay (s)</label>
          <input
            type="number"
            required
            min="0"
            value={formData.delay_s ?? 0}
            onChange={(e) => setFormData({ ...formData, delay_s: parseInt(e.target.value) })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          />
        </div>

        <div className="col-span-3 rounded-xl border border-gray-200 bg-gray-50 p-4 flex flex-col gap-3">
          <span className="text-sm font-semibold text-gray-700 flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-blue-600" fill="currentColor" strokeWidth={0} />Generate mock data with AI <span className="font-normal text-gray-500">(optional)</span></span>
          <textarea
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder='e.g. "3 products with id, name, and price"'
            className="px-3 py-2.5 rounded-xl border border-violet-200 text-sm bg-white min-h-[72px] resize-none"
          />
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || !aiPrompt.trim()}
              className="px-5 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-2"
            >
              {isGenerating && (
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              )}
              {isGenerating ? 'Generating…' : 'Generate'}
            </button>
            {aiError && <span className="text-red-600 text-sm">{aiError}</span>}
          </div>
        </div>

        <div className="col-span-3 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <label className="text-sm font-semibold text-zinc-600">Response Body (JSON)</label>
              {!(formData.use_mock_backend ?? true) && (
                <span className="text-xs text-zinc-400">Leave empty to use real server response</span>
              )}
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-300 text-xs font-medium text-zinc-600 hover:bg-zinc-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Upload JSON
            </button>
            <input ref={fileInputRef} type="file" accept=".json,application/json" className="hidden" onChange={handleFileUpload} />
          </div>
          <textarea
            value={mockDataJson}
            onChange={(e) => handleJsonChange(e.target.value)}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm font-mono min-h-[120px] bg-white"
          />
          {jsonError && <span className="text-red-600 text-sm">{jsonError}</span>}
        </div>

        <BackendModeSelector
          value={formData.use_mock_backend ?? true}
          onChange={(v) => setFormData({ ...formData, use_mock_backend: v })}
        />

        <div className="col-span-3 flex flex-col gap-3">
          {submitError && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 text-sm">
              {submitError}
            </div>
          )}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={!!jsonError || isSaving}
              className="px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold disabled:opacity-50"
            >
              {isSaving ? 'Saving…' : 'Save Changes'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 rounded-xl border border-zinc-300 text-zinc-700 font-semibold hover:bg-zinc-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

// ── Create form ───────────────────────────────────────────────────────────────

function CreateRuleForm({ onSubmit, submitError }: { onSubmit: (rule: RuleCreate) => void; submitError?: string | null }) {
  const [formData, setFormData] = useState<RuleCreate>({
    name: '',
    url_pattern: '',
    method: 'GET',
    delay_s: 0,
    mock_data: {},
    use_mock_backend: false,
  })
  const [mockDataJson, setMockDataJson] = useState('{\n  \n}')
  const [jsonError, setJsonError] = useState<string | null>(null)
  const [aiPrompt, setAiPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const userHasSetBackend = useRef(false)

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const text = ev.target?.result as string
      handleJsonChange(text)
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const parsed = JSON.parse(mockDataJson)
      onSubmit({ ...formData, mock_data: parsed, ai_prompt: aiPrompt || undefined })
    } catch {
      setJsonError('Invalid JSON format')
    }
  }

  const handleJsonChange = (value: string) => {
    setMockDataJson(value)
    try {
      const parsed = JSON.parse(value)
      setFormData((prev) => ({
        ...prev,
        mock_data: parsed,
        ...(!userHasSetBackend.current && { use_mock_backend: computeUseMockBackend(prev.status_code ?? undefined, value) }),
      }))
      setJsonError(null)
    } catch {
      setJsonError('Invalid JSON format')
    }
  }

  const handleGenerate = async () => {
    if (!aiPrompt.trim()) return
    setIsGenerating(true)
    setAiError(null)
    try {
      const result = await aiApi.generateMockData(aiPrompt, formData.url_pattern, formData.method)
      const pretty = JSON.stringify(result.mock_data, null, 2)
      setMockDataJson(pretty)
      setFormData((prev) => ({
        ...prev,
        mock_data: result.mock_data,
        ...(!userHasSetBackend.current && { use_mock_backend: computeUseMockBackend(prev.status_code ?? undefined, pretty) }),
      }))
      setJsonError(null)
    } catch {
      setAiError('Failed to generate data. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200 mb-6">
      <h2 className="text-xl font-semibold mb-4">Create New Rule</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-3 gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Rule Name <span className="text-red-500">*</span></label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="col-span-2 flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Endpoint Pattern <span className="text-red-500">*</span></label>
          <input
            type="text"
            required
            placeholder="/api/orders/*"
            value={formData.url_pattern}
            onChange={(e) => setFormData({ ...formData, url_pattern: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Method</label>
          <select
            value={formData.method}
            onChange={(e) => setFormData({ ...formData, method: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm bg-white"
          >
            {['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'ANY'].map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Status Code</label>
          <input
            type="number"
            min="100"
            max="599"
            placeholder="None"
            value={formData.status_code ?? ''}
            onChange={(e) => {
              const sc = e.target.value === '' ? null : parseInt(e.target.value)
              setFormData((prev) => ({
                ...prev,
                status_code: sc,
                ...(!userHasSetBackend.current && { use_mock_backend: computeUseMockBackend(sc ?? undefined, mockDataJson) }),
              }))
            }}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Delay (s)</label>
          <input
            type="number"
            required
            min="0"
            value={formData.delay_s}
            onChange={(e) => setFormData({ ...formData, delay_s: parseInt(e.target.value) })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="col-span-3 rounded-xl border border-gray-200 bg-gray-50 p-4 flex flex-col gap-3">
          <span className="text-sm font-semibold text-gray-700 flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-blue-600" fill="currentColor" strokeWidth={0} />Generate mock data with AI <span className="font-normal text-gray-500">(optional)</span></span>
          <textarea
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder='e.g. "3 products with id, name, and price"'
            className="px-3 py-2.5 rounded-xl border border-violet-200 text-sm bg-white min-h-[72px] resize-none"
          />
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || !aiPrompt.trim()}
              className="px-5 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold disabled:opacity-50 flex items-center gap-2"
            >
              {isGenerating && (
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              )}
              {isGenerating ? 'Generating…' : 'Generate'}
            </button>
            {aiError && <span className="text-red-600 text-sm">{aiError}</span>}
          </div>
        </div>

        <div className="col-span-3 flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <label className="text-sm font-semibold text-zinc-600">Response Body (JSON)</label>
              {!formData.use_mock_backend && (
                <span className="text-xs text-zinc-400">Leave empty to use real server response</span>
              )}
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-300 text-xs font-medium text-zinc-600 hover:bg-zinc-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Upload JSON
            </button>
            <input ref={fileInputRef} type="file" accept=".json,application/json" className="hidden" onChange={handleFileUpload} />
          </div>
          <textarea
            value={mockDataJson}
            onChange={(e) => handleJsonChange(e.target.value)}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm font-mono min-h-[120px]"
            placeholder='{\n  "message": "Hello",\n  "data": {\n    "id": 123\n  }\n}'
          />
          {jsonError && (
            <span className="text-red-600 text-sm">{jsonError}</span>
          )}
        </div>

        <BackendModeSelector
          value={formData.use_mock_backend}
          onChange={(v) => {
            userHasSetBackend.current = true
            setFormData((prev) => ({ ...prev, use_mock_backend: v }))
          }}
        />

        <div className="col-span-3 flex flex-col gap-3">
          {submitError && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700 text-sm">
              {submitError}
            </div>
          )}
          <div className="flex items-end">
            <button
              type="submit"
              disabled={!!jsonError}
              className="px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold disabled:opacity-50"
            >
              Save Rule
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
