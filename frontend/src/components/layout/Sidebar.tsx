import { NavLink } from 'react-router-dom'

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/rules', label: 'Rules' },
  { path: '/api-keys', label: 'API Keys' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white p-7 flex-shrink-0">
      <div className="mb-8">
        <div className="text-2xl font-bold mb-1.5">MockEngine</div>
        <div className="text-zinc-400 text-sm">SDK Management Portal</div>
      </div>

      <nav className="flex flex-col gap-2.5">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block px-4 py-3 rounded-xl text-zinc-300 text-base no-underline transition-colors ${
                isActive ? 'bg-slate-800 text-white' : 'hover:bg-slate-800'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
