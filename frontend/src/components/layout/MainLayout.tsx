import { Routes, Route } from 'react-router-dom'
import Sidebar from './Sidebar'
import Dashboard from "../../pages/Dashboard.tsx";
import Rules from '../../pages/Rules.tsx'
import ApiKeys from '../../pages/ApiKeys.tsx'

export default function MainLayout() {
  return (
    <div className="flex min-h-screen bg-neutral-100">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/api-keys" element={<ApiKeys />} />
        </Routes>
      </main>
    </div>
  )
}
