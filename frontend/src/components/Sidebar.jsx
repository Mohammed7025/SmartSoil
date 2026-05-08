import React, { useState } from 'react';
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
    Bot,
    LogOut,
    Sparkles,
    Beaker,
    Menu,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';

const Sidebar = () => {
    const { currentUser, logout } = useAuth();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const navSections = [
        {
            title: 'Dashboards',
            items: [
                { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' }
            ]
        },
        {
            title: 'AI Tools',
            items: [
                { icon: Leaf, label: 'Crop Recommender', path: '/analysis' },
                { icon: Beaker, label: 'Fertilizer Optimizer', path: '/analysis' },
                { icon: Droplets, label: 'Irrigation Scheduler', path: '/analysis' },
            ]
        },
        {
            title: 'More',
            items: [
                { icon: Activity, label: 'Live Sensor Data', path: '/live-data' },
                { icon: Brain, label: 'Explainable AI', path: '/explainable-ai' },
                { icon: Bot, label: 'AGROBOT', path: '/advisor' },
                { icon: Settings, label: 'Settings', path: '/settings' }
            ]
        }
    ];

    if (currentUser?.role === 'admin') {
        navSections[2].items.unshift({ icon: Users, label: 'Admin Panel', path: '/admin' });
    }

    return (
        <aside className={`sidebar flex-shrink-0 z-20 ${isCollapsed ? 'collapsed' : ''}`}>
            {/* Logo Area */}
            <div className={`logo-area flex items-center ${isCollapsed ? 'justify-center px-0' : 'gap-3 px-2'} relative transition-all duration-300`}>
                <div className="logo-icon shrink-0">
                    <Leaf size={20} />
                </div>
                {!isCollapsed && (
                    <div className="min-w-0 flex-1">
                        <h1 className="h3 truncate" style={{ fontSize: '1.1rem', marginBottom: 0 }}>Smart Soil</h1>
                        <p className="text-muted text-small truncate">Web Dashboard</p>
                    </div>
                )}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className={`absolute ${isCollapsed ? '-right-6 top-5 shadow-sm border border-border-color bg-white' : 'right-0'} p-1 hover:bg-[#7C6F64]/10 rounded-full text-[#6B6259] transition-all z-50 shrink-0 toggle-btn`}
                    title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
                >
                    {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={18} />}
                </button>
            </div>

            {/* Navigation */}
            <nav className="nav-list overflow-y-auto">
                {navSections.map((section) => (
                    <div key={section.title} className="nav-section mb-6">
                        {!isCollapsed ? (
                            <h2 className="px-4 text-[10px] font-bold uppercase tracking-widest text-[#6B6259] mb-3 truncate">
                                {section.title}
                            </h2>
                        ) : (
                            <div className="h-[2px] w-6 bg-border-color mx-auto mb-3 rounded-full" />
                        )}
                        <div className="flex flex-col gap-1">
                            {section.items.map((item) => (
                                <NavLink
                                    key={item.label}
                                    to={item.path}
                                    className={({ isActive }) => `nav-item ${isActive ? 'active' : ''} ${isCollapsed ? 'justify-center !px-0' : ''}`}
                                    title={isCollapsed ? item.label : undefined}
                                >
                                    <item.icon size={18} className="shrink-0" />
                                    {!isCollapsed && <span className="truncate">{item.label}</span>}
                                </NavLink>
                            ))}
                        </div>
                    </div>
                ))}
            </nav>

            {/* User Info / Footer */}
            <div className={`user-area flex items-center ${isCollapsed ? 'flex-col gap-4 px-0 justify-center' : 'gap-3 px-2'} mt-auto pt-4 border-t border-border-color pb-2 transition-all duration-300`}>
                <div className="avatar shrink-0">
                    {currentUser?.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                        <p className="text-small truncate" style={{ fontWeight: 600 }}>{currentUser?.full_name || 'User'}</p>
                        <p className="text-muted text-small truncate" style={{ fontSize: '0.75rem' }}>{currentUser?.role || 'Farmer'}</p>
                    </div>
                )}
                <button
                    onClick={logout}
                    className={`p-2 hover:bg-[#7C6F64]/10 rounded-full text-[#6B6259] hover:text-[#7C6F64] transition-colors ${isCollapsed ? '' : 'shrink-0'}`}
                    title="Logout"
                >
                    <LogOut size={16} />
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
