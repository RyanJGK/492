import { Shield, Activity } from 'lucide-react'
import { useUser } from '../context/UserContext'

export default function Navbar() {
  const { user } = useUser()

  return (
    <nav className="bg-gradient-to-r from-blue-900 to-blue-700 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold">492-Energy-Defense</h1>
              <p className="text-xs text-blue-200">
                Real-Time Cyber Defense Platform
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-green-400" />
              <span className="text-sm">System Operational</span>
            </div>
            
            {user && (
              <div className="bg-blue-800 px-4 py-2 rounded-lg">
                <div className="text-xs text-blue-300">Current Role</div>
                <div className="font-semibold capitalize">{user.role}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
