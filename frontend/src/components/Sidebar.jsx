import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    LayoutDashboard,
    Activity,
    Droplets,
    Brain,
    Settings,
    Users,
    Leaf,
    LogOut
} from 'lucide-react';

const Sidebar = () => {
    const { currentUser, logout } = useAuth();

    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
        { icon: Activity, label: 'Live Sensor Data', path: '/live-data' },
        { icon: Leaf, label: 'AI Recommendations', path: '/analysis' },
        { icon: Droplets, label: 'Irrigation Control', path: '/irrigation' },
        { icon: Brain, label: 'Explainable AI', path: '/explainable-ai' },
        // { icon: Users, label: 'Users', path: '/users' },
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    if (currentUser?.role === 'admin') {
        navItems.splice(5, 0, { icon: Users, label: 'Admin Panel', path: '/admin' });
    }

    return (
        <aside className="sidebar">
            {/* Logo Area */}
            <div className="logo-area">
                <div className="logo-icon">
                    <Leaf size={20} />
                </div>
                <div>
                    <h1 className="h3" style={{ fontSize: '1.1rem', marginBottom: 0 }}>Smart Soil</h1>
                    <p className="text-muted text-small">Web Dashboard</p>
                </div>
            </div>

            {/* Navigation */}
            <nav className="nav-list">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    >
                        <item.icon size={18} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            {/* User Info / Footer */}
            <div className="user-area">
                <div className="avatar">
                    {currentUser?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-small truncate" style={{ fontWeight: 600 }}>{currentUser?.full_name || 'User'}</p>
                    <p className="text-muted text-small truncate" style={{ fontSize: '0.75rem' }}>{currentUser?.role || 'Farmer'}</p>
                </div>
                <button
                    onClick={logout}
                    className="p-2 hover:bg-white/10 rounded-full text-[hsl(var(--text-muted))] hover:text-red-400 transition-colors"
                    title="Logout"
                >
                    <LogOut size={16} />
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
