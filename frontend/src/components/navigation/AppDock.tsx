import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Home, 
  GraduationCap, 
  MessageSquare, 
  BarChart3, 
  Settings, 
  User,
  Trophy,
  LogOut
} from 'lucide-react';
import Dock, { DockItemData } from './Dock';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';

export default function AppDock() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast({ title: "Logged out", description: "You've been logged out successfully" });
    navigate('/auth');
  };

  const items: DockItemData[] = [
    {
      icon: <Home size={20} />,
      label: 'Home',
      onClick: () => navigate('/'),
      className: location.pathname === '/' ? 'active' : ''
    },
    {
      icon: <GraduationCap size={20} />,
      label: 'Training',
      onClick: () => navigate('/training'),
      className: location.pathname.startsWith('/training') ? 'active' : ''
    },
    {
      icon: <MessageSquare size={20} />,
      label: 'Chat',
      onClick: () => navigate('/chat'),
      className: location.pathname === '/chat' ? 'active' : ''
    },
    {
      icon: <BarChart3 size={20} />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard'),
      className: location.pathname === '/dashboard' ? 'active' : ''
    },
    {
      icon: <Trophy size={20} />,
      label: 'Analytics',
      onClick: () => navigate('/analytics'),
      className: location.pathname === '/analytics' ? 'active' : ''
    },
    {
      icon: <User size={20} />,
      label: 'Profile',
      onClick: () => navigate('/settings'),
      className: location.pathname === '/settings' ? 'active' : ''
    },
    {
      icon: <Settings size={20} />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
      className: location.pathname === '/settings' ? 'active' : ''
    }
  ];

  // Add logout button if authenticated
  if (isAuthenticated) {
    items.push({
      icon: <LogOut size={20} />,
      label: 'Logout',
      onClick: handleLogout,
      className: 'logout-item'
    });
  }

  return (
    <Dock
      items={items}
      panelHeight={68}
      baseItemSize={50}
      magnification={70}
      distance={150}
    />
  );
}
