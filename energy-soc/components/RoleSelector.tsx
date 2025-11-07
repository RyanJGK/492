import React from 'react'
import { Shield, Eye, Settings } from 'lucide-react'
import { UserRole } from '@/app/page'

interface RoleSelectorProps {
  currentRole: UserRole
  onRoleChange: (role: UserRole) => void
}

export default function RoleSelector({ currentRole, onRoleChange }: RoleSelectorProps) {
  const roles: Array<{ id: UserRole; label: string; icon: React.ReactNode; description: string }> = [
    {
      id: 'admin',
      label: 'Admin',
      icon: <Settings className="w-4 h-4" />,
      description: 'Full control, AI weight configuration'
    },
    {
      id: 'analyst',
      label: 'Analyst',
      icon: <Shield className="w-4 h-4" />,
      description: 'Investigate alerts, evaluate AI results'
    },
    {
      id: 'observer',
      label: 'Observer',
      icon: <Eye className="w-4 h-4" />,
      description: 'Read-only monitoring and reporting'
    }
  ]

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-slate-400 mr-2">Role:</span>
      <div className="flex gap-2">
        {roles.map((role) => (
          <button
            key={role.id}
            onClick={() => onRoleChange(role.id)}
            className={`
              flex items-center gap-2 px-4 py-2 rounded-lg transition-all
              ${currentRole === role.id
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }
            `}
            title={role.description}
          >
            {role.icon}
            <span className="font-medium">{role.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
