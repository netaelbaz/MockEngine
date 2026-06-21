import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiKeysApi } from '../lib/api'
import type { ApiKeyCreate } from '../types'

export default function ApiKeys() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeysApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: (keyData: ApiKeyCreate) => apiKeysApi.create(keyData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setShowCreateForm(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (keyId: string) => apiKeysApi.delete(keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const toggleStatusMutation = useMutation({
    mutationFn: ({ keyId, isActive }: { keyId: string; isActive: boolean }) =>
      apiKeysApi.updateStatus(keyId, !isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const filteredKeys = apiKeys?.filter((key) =>
    key.name.toLowerCase().includes(search.toLowerCase())
  ) || []

  const copyToClipboard = async (key: string, keyId: string) => {
    await navigator.clipboard.writeText(key)
    setCopiedKey(keyId)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  if (isLoading) {
    return <div className="text-center py-12 text-zinc-500">Loading...</div>
  }

  return (
    <div>
      <div className="mb-7">
        <div className="text-zinc-500 text-sm mb-1.5">API Keys</div>
        <h1 className="text-3xl mb-2">API Key Management</h1>
        <p className="text-zinc-600 text-base mb-4">
          Generate and manage keys used by applications that integrate the SDK.
        </p>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-5 py-3 rounded-xl bg-slate-900 text-white font-semibold"
        >
          {showCreateForm ? 'Cancel' : 'Generate Key'}
        </button>
      </div>

      {showCreateForm && (
        <CreateKeyForm
          onSubmit={(keyData) => createMutation.mutate(keyData)}
          isLoading={createMutation.isPending}
        />
      )}

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200">
        <div className="flex justify-between items-center mb-5">
          <input
            type="text"
            placeholder="Search API keys by name"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-80 px-4 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-200">
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Name</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Key Preview</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Created</th>
              <th className="text-left py-4 px-4 text-sm text-zinc-600 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredKeys.map((key) => (
              <tr key={key.id} className="border-b border-zinc-200 hover:bg-neutral-50">
                <td className="py-4 px-4 font-medium">{key.name}</td>
                <td className="py-4 px-4">
                  <code className="text-sm">
                    {`${key.api_key.slice(0, 12)}...${key.api_key.slice(-6)}`}
                  </code>
                </td>
                <td className="py-4 px-4 text-sm">
                  {new Date(key.created_at).toLocaleDateString()}
                </td>
                <td className="py-4 px-4">
                  <div className="flex gap-2">
                    {(
                      <button
                        onClick={() => copyToClipboard(key.api_key, key.id.toString())}
                        className="p-2 rounded-lg bg-indigo-100 text-indigo-700 hover:bg-indigo-200"
                        title={copiedKey === key.id.toString() ? 'Copied!' : 'Copy to clipboard'}
                      >
                        {copiedKey === key.id.toString() ? (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(key.id.toString())}
                      className="p-2 rounded-lg bg-red-100 text-red-700 hover:bg-red-200"
                      title="Delete"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CreateKeyForm({
  onSubmit,
  isLoading,
}: {
  onSubmit: (keyData: ApiKeyCreate) => void
  isLoading: boolean
}) {
  const [keyName, setKeyName] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ key_name: keyName })
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-zinc-200 mb-6">
      <h2 className="text-xl font-semibold mb-4">Generate New API Key</h2>
      <form onSubmit={handleSubmit} className="flex gap-4 items-end">
        <div className="flex flex-col gap-2 flex-1">
          <label className="text-sm font-semibold text-zinc-600">Key Name</label>
          <input
            type="text"
            required
            placeholder="Example: Android QA Team"
            value={keyName}
            onChange={(e) => setKeyName(e.target.value)}
            className="px-3 py-3 rounded-xl border border-zinc-300 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-3 rounded-xl bg-slate-900 text-white font-semibold disabled:opacity-50"
        >
          {isLoading ? 'Generating...' : 'Generate Key'}
        </button>
      </form>
    </div>
  )
}
