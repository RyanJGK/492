import { useState, useEffect } from 'react'
import { UserCircle, ChevronDown } from 'lucide-react'
import { useUser } from '../context/UserContext'
import axios from 'axios'

export default function RoleSelector() {
  const { user, switchRole } = useUser()
  const [roles, setRoles] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    axios.get('/api/auth/roles')
      .then(response => setRoles(response.data.roles))
      .catch(error => console.error('Failed to fetch roles:', error))
  }, [])

  const handleRoleChange = async (role) => {
    await switchRole(role)
    setShowDropdown(false)
  }

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-purple-600'
      case 'analyst': return 'bg-blue-600'
      case 'observer': return 'bg-green-600'
      default: return 'bg-gray-600'
    }
  }

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-purple-100 text-purple-800 border-purple-300'
      case 'analyst': return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'observer': return 'bg-green-100 text-green-800 border-green-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  if (!user) return null

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <UserCircle className="w-5 h-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">
                Role View:
              </span>
            </div>
            
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${getRoleColor(user.role)} text-white hover:opacity-90 transition-opacity`}
              >
                <span className="font-semibold capitalize">{user.role}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {showDropdown && (
                <div className="absolute top-full mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                  {roles.map((roleInfo) => (
                    <button
                      key={roleInfo.name}
                      onClick={() => handleRoleChange(roleInfo.name)}
                      className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${
                        user.role === roleInfo.name ? 'bg-blue-50' : ''
                      } first:rounded-t-lg last:rounded-b-lg border-b border-gray-100 last:border-b-0`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold capitalize text-gray-900">
                          {roleInfo.name}
                        </span>
                        {user.role === roleInfo.name && (
                          <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-600 mb-2">
                        {roleInfo.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {roleInfo.capabilities.slice(0, 3).map((cap, idx) => (
                          <span
                            key={idx}
                            className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="text-sm text-gray-600">
            <span className="font-medium">User:</span> {user.username}
          </div>
        </div>
      </div>
    </div>
  )
}
