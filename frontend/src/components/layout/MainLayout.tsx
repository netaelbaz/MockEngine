import { Routes, Route } from 'react-router-dom'
import Sidebar from './Sidebar'
import Dashboard from '../../pages/Dashboard'
import Rules from '../../pages/Rules'
import ApiKeys from '../../pages/ApiKeys'

export default function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-neutral-100">
      <Sidebar />
      <main className="flex-1 h-screen overflow-y-auto p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/api-keys" element={<ApiKeys />} />
        </Routes>
      </main>
    </div>
  )
}
