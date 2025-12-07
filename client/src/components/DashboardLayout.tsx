'use client';

import { useAuth } from '@/contexts/AuthContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ChevronDown, LogOut, User, Settings, Search } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-[#8E1B1B] border-b sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Left Side - Logo & Nav */}
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center p-1">
                  <svg viewBox="0 0 100 100" className="w-full h-full">
                    <circle cx="50" cy="50" r="45" fill="#8E1B1B"/>
                    <text x="50" y="65" fontSize="40" fill="white" textAnchor="middle" fontWeight="bold">U</text>
                  </svg>
                </div>
                <span className="font-bold text-white text-lg">
                  {user?.role === 'student' ? 'Student Portal' : user?.role === 'admin' ? 'Admin' : 'Faculty'}
                </span>
              </div>
              {(user?.role === 'admin' || user?.role === 'faculty') && (
                <div className="hidden md:flex items-center gap-6">
                  <a href="/dashboard" className="text-sm font-medium text-white hover:text-gray-200">
                    Dashboard
                  </a>
                  <a href="/dashboard/responses" className="text-sm text-gray-200 hover:text-white">
                    Responses
                  </a>
                </div>
              )}
            </div>

            {/* Right Side - Search & User */}
            <div className="flex items-center gap-4">
              {(user?.role === 'admin' || user?.role === 'faculty') && (
                <div className="relative hidden lg:block">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search..."
                    className="pl-10 w-[300px] bg-white/10 border-white/20 text-white placeholder:text-gray-300"
                  />
                </div>
              )}

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="gap-2 hover:bg-white/10 text-white">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-[#8E1B1B] font-bold">
                      {user?.username?.charAt(0).toUpperCase()}
                    </div>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col">
                      <span className="font-medium">{user?.username}</span>
                      <span className="text-xs text-gray-500">{user?.email}</span>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout} className="text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {children}
    </div>
  );
}
