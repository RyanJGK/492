'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import RoleSelector from '@/components/RoleSelector'
import AdminView from '@/components/views/AdminView'
import AnalystView from '@/components/views/AnalystView'
import ObserverView from '@/components/views/ObserverView'

export type UserRole = 'admin' | 'analyst' | 'observer'

export default function Home() {
  const [currentRole, setCurrentRole] = useState<UserRole>('analyst')

  const renderView = () => {
    switch (currentRole) {
      case 'admin':
        return <AdminView />
      case 'analyst':
        return <AnalystView />
      case 'observer':
        return <ObserverView />
      default:
        return <AnalystView />
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col h-full">
        {/* Header with Role Selector */}
        <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                Energy SOC Dashboard
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                AI-Powered Security Operations Center - Puget Sound Energy Infrastructure
              </p>
            </div>
            <RoleSelector currentRole={currentRole} onRoleChange={setCurrentRole} />
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 overflow-auto bg-slate-950">
          {renderView()}
        </div>
      </div>
    </DashboardLayout>
  )
}
