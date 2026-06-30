import { createContext, useContext, useState, ReactNode } from 'react'

interface AuthUser {
  firstName: string
  lastName: string
  email: string
}

interface AuthContextType {
  token: string | null
  user: AuthUser | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

interface TokenResponse {
  access_token: string
  first_name: string
  last_name: string
  email: string
}

async function authFetch(path: string, body: object): Promise<TokenResponse> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const isJson = res.headers.get('content-type')?.includes('application/json')
    if (isJson) {
      const data = await res.json()
      throw new Error(data.detail || 'Request failed')
    }
    throw new Error(`Request failed (${res.status})`)
  }
  return res.json() as Promise<TokenResponse>
}

function loadUser(): AuthUser | null {
  const raw = localStorage.getItem('auth_user')
  if (!raw) return null
  try { return JSON.parse(raw) as AuthUser } catch { return null }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('auth_token'))
  const [user, setUser] = useState<AuthUser | null>(loadUser)

  const persist = (t: string, u: AuthUser) => {
    localStorage.setItem('auth_token', t)
    localStorage.setItem('auth_user', JSON.stringify(u))
    setToken(t)
    setUser(u)
  }

  const login = async (email: string, password: string) => {
    const data = await authFetch('/api/v1/auth/login', { email, password })
    persist(data.access_token, { firstName: data.first_name, lastName: data.last_name, email: data.email })
  }

  const register = async (email: string, password: string, firstName: string, lastName: string) => {
    const data = await authFetch('/api/v1/auth/register', { email, password, first_name: firstName, last_name: lastName })
    persist(data.access_token, { firstName: data.first_name, lastName: data.last_name, email: data.email })
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
