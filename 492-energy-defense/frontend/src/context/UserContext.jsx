import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const UserContext = createContext()

export function UserProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const switchRole = async (role) => {
    try {
      const response = await axios.post('/api/auth/switch-role', { role })
      setUser(response.data)
      localStorage.setItem('userRole', role)
    } catch (error) {
      console.error('Failed to switch role:', error)
    }
  }

  useEffect(() => {
    // Initialize with default role
    const savedRole = localStorage.getItem('userRole') || 'admin'
    switchRole(savedRole).finally(() => setLoading(false))
  }, [])

  return (
    <UserContext.Provider value={{ user, switchRole, loading }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within UserProvider')
  }
  return context
}
