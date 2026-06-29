import { useState, useRef, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/rules', label: 'Rules' },
  { path: '/api-keys', label: 'API Keys' },
]

function Initials({ firstName, lastName }: { firstName: string; lastName: string }) {
  const a = firstName.charAt(0).toUpperCase()
  const b = lastName.charAt(0).toUpperCase()
  const label = a || b ? `${a}${b}` : null
  return (
    <div className="w-9 h-9 rounded-full bg-indigo-500 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
      {label ?? (
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      )}
    </div>
  )
}

export default function Sidebar() {
  const { logout, user } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    if (menuOpen) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [menuOpen])

  return (
    <aside className="w-52 bg-slate-900 text-white p-5 flex-shrink-0 flex flex-col">
      <div className="mb-8">
        <div className="text-2xl font-bold mb-1.5">MockEngine</div>
        <div className="text-zinc-400 text-sm">SDK Management Portal</div>
      </div>

      <nav className="flex flex-col gap-2.5 flex-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `block px-4 py-3 rounded-xl text-zinc-300 text-base no-underline transition-colors ${
                isActive ? 'bg-indigo-600 text-white' : 'hover:bg-slate-800'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="relative mt-2" ref={menuRef}>
        {menuOpen && (
          <div className="absolute bottom-full left-0 right-0 mb-2 bg-slate-800 rounded-xl overflow-hidden shadow-lg border border-slate-700">
            <button
              onClick={() => { setMenuOpen(false); logout() }}
              className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-zinc-300 hover:bg-slate-700 hover:text-white transition-colors"
            >
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign out
            </button>
          </div>
        )}

        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-slate-800 transition-colors w-full text-left group"
        >
          <Initials firstName={user?.firstName ?? ''} lastName={user?.lastName ?? ''} />
          <div className="min-w-0 flex-1">
            <div className="text-sm font-semibold text-white truncate">
              {user ? `${user.firstName} ${user.lastName}` : 'Account'}
            </div>
            <div className="text-xs text-zinc-500 group-hover:text-zinc-400 transition-colors truncate">
              {user?.email ?? ''}
            </div>
          </div>
          <svg
            width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
            className={`text-zinc-500 flex-shrink-0 transition-transform ${menuOpen ? 'rotate-180' : ''}`}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
          </svg>
        </button>
      </div>
    </aside>
  )
}
