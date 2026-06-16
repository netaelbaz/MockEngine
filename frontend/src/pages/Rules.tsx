import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { rulesApi } from '../lib/api'
import type { Rule, RuleCreate, RuleMode } from '../types'

export default function Rules() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: () => rulesApi.list(),
    refetchInterval: 180000, // 3 minutes
  })

  const createMutation = useMutation({
    mutationFn: (rule: RuleCreate) => rulesApi.create(rule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] })
      setShowCreateForm(false)
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
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-5 py-3 rounded-xl bg-slate-900 text-white font-semibold"
        >
          {showCreateForm ? 'Cancel' : 'New Rule'}
        </button>
      </div>

      {showCreateForm && <CreateRuleForm onSubmit={(rule) => createMutation.mutate(rule)} />}

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200">
        <div className="flex justify-between items-center mb-5">
          <input
            type="text"
            placeholder="Search rules by endpoint, name or mode"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Mode</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Enabled</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredRules.map((rule) => (
              <tr key={rule.id} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{rule.name}</td>
                <td className="py-4 px-4">
                  <span className="px-3 py-1 rounded-full border border-zinc-300 text-xs font-semibold">
                    {rule.url_pattern.split(' ')[0] || 'GET'}
                  </span>
                </td>
                <td className="py-4 px-4">{rule.url_pattern}</td>
                <td className="py-4 px-4">{rule.status_code}</td>
                <td className="py-4 px-4">{rule.delay_ms} ms</td>
                <td className="py-4 px-4">{rule.mode}</td>
                <td className="py-4 px-4">
                  <button
                    onClick={() => toggleMutation.mutate({ ruleId: rule.id.toString(), isEnabled: rule.is_enabled })}
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
                  <button
                    onClick={() => deleteMutation.mutate(rule.id.toString())}
                    className="px-3 py-2 rounded-lg bg-red-100 text-red-700 font-medium text-sm"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CreateRuleForm({ onSubmit }: { onSubmit: (rule: RuleCreate) => void }) {
  const [formData, setFormData] = useState<RuleCreate>({
    name: '',
    url_pattern: '',
    status_code: 200,
    delay_ms: 0,
    mode: 'always',
    mock_data: {},
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200 mb-6">
      <h2 className="text-xl font-semibold mb-4">Create New Rule</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-3 gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Rule Name</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Status Code</label>
          <input
            type="number"
            required
            min="100"
            max="599"
            value={formData.status_code}
            onChange={(e) => setFormData({ ...formData, status_code: parseInt(e.target.value) })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Delay (ms)</label>
          <input
            type="number"
            required
            min="0"
            value={formData.delay_ms}
            onChange={(e) => setFormData({ ...formData, delay_ms: parseInt(e.target.value) })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <div className="col-span-3 flex flex-col gap-2">
          <label className="text-sm font-semibold text-zinc-600">Endpoint Pattern</label>
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
          <label className="text-sm font-semibold text-zinc-600">Mode</label>
          <select
            value={formData.mode}
            onChange={(e) => setFormData({ ...formData, mode: e.target.value as RuleMode })}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          >
            <option value="always">Always</option>
            <option value="user_controlled">User Controlled</option>
            <option value="percentage">Percentage</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            className="px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold"
          >
            Save Rule
          </button>
        </div>
      </form>
    </div>
  )
}
