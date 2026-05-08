import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Users, Sprout, Calendar, ChevronRight, Trash2, PieChart, Activity, ShieldCheck } from 'lucide-react';

const AdminDashboard = () => {
    const { currentUser } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [userHistory, setUserHistory] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('users'); // 'users', 'logs', 'analytics'

    useEffect(() => {
        if (!currentUser || currentUser.role !== 'admin') {
            navigate('/dashboard');
            return;
        }
        fetchInitialData();
    }, [currentUser, navigate]);

    const fetchInitialData = async () => {
        setLoading(true);
        setError(null);
        try {
            await Promise.all([fetchUsers(), fetchStats()]);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await fetch('http://localhost:8000/admin/users', {
                headers: { 'user-id': currentUser.id }
            });
            if (res.ok) {
                const data = await res.json();
                setUsers(data);
            } else {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Failed to fetch users: ${res.status}`);
            }
        } catch (error) {
            console.error("Failed to fetch users", error);
            throw error;
        }
    };

    const fetchStats = async () => {
        try {
            const res = await fetch('http://localhost:8000/admin/stats', {
                headers: { 'user-id': currentUser.id }
            });
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            } else {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Failed to fetch stats: ${res.status}`);
            }
        } catch (error) {
            console.error("Failed to fetch stats", error);
            throw error;
        }
    };

    const fetchUserHistory = async (userId) => {
        try {
            const res = await fetch(`http://localhost:8000/admin/users/${userId}/history`, {
                headers: { 'user-id': currentUser.id }
            });
            if (res.ok) {
                const data = await res.json();
                setSelectedUser(data.user);
                setUserHistory(data.history);
            }
        } catch (error) {
            console.error("Failed to fetch history", error);
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!window.confirm("Are you sure you want to delete this user and all their data? This action cannot be undone.")) return;

        try {
            const res = await fetch(`http://localhost:8000/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'user-id': currentUser.id }
            });
            if (res.ok) {
                setUsers(users.filter(u => u.id !== userId));
                if (selectedUser?.id === userId) {
                    setSelectedUser(null);
                    setUserHistory([]);
                }
                fetchStats(); // Refresh stats
            }
        } catch (error) {
            console.error("Deletion failed", error);
        }
    };

    if (loading && !users.length) return <div className="p-10 text-center text-white">Loading Admin Panel...</div>;

    return (
        <div className="container py-10 min-h-screen">
            {error && (
                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 flex items-center gap-3">
                    <Activity className="w-5 h-5" />
                    <div>
                        <p className="font-bold">Error loading data</p>
                        <p className="text-sm">{error}</p>
                    </div>
                    <button
                        onClick={fetchInitialData}
                        className="ml-auto px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-xs transition-colors"
                    >
                        Retry
                    </button>
                </div>
            )}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="h2 mb-1 flex items-center gap-2">
                        <ShieldCheck className="text-[hsl(var(--primary))]" /> Admin Dashboard
                    </h1>
                    <p className="text-muted">Manage users, monitor system health, and view analytics.</p>
                </div>

                <div className="flex bg-white/5 p-1 rounded-xl border border-white/5">
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'users' ? 'bg-[hsl(var(--primary))] text-white' : 'text-muted hover:text-white'}`}
                    >
                        Users
                    </button>
                    <button
                        onClick={() => setActiveTab('analytics')}
                        className={`px-4 py-2 rounded-lg text-sm transition-all ${activeTab === 'analytics' ? 'bg-[hsl(var(--primary))] text-white' : 'text-muted hover:text-white'}`}
                    >
                        Analytics
                    </button>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card border-l-4 border-[hsl(var(--primary))]">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-muted text-sm uppercase tracking-wider font-bold">Total Farmers</p>
                            <h2 className="h2 mt-1">{stats?.total_users || 0}</h2>
                        </div>
                        <Users className="w-8 h-8 text-[hsl(var(--primary))] opacity-50" />
                    </div>
                </div>
                <div className="card border-l-4 border-emerald-500">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-muted text-sm uppercase tracking-wider font-bold">Total Readings</p>
                            <h2 className="h2 mt-1">{stats?.total_readings || 0}</h2>
                        </div>
                        <Activity className="w-8 h-8 text-emerald-500 opacity-50" />
                    </div>
                </div>
                <div className="card border-l-4 border-amber-500">
                    <div className="flex justify-between items-center">
                        <div>
                            <p className="text-muted text-sm uppercase tracking-wider font-bold">Active (7 Days)</p>
                            <h2 className="h2 mt-1">{stats?.active_users_7d || 0}</h2>
                        </div>
                        <PieChart className="w-8 h-8 text-amber-500 opacity-50" />
                    </div>
                </div>
            </div>

            {activeTab === 'users' ? (
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-8">
                    {/* User List */}
                    <div className="card h-fit">
                        <h3 className="h3 mb-4 flex items-center gap-2">
                            Registered Users
                        </h3>
                        <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                            {users.map(u => (
                                <div
                                    key={u.id}
                                    onClick={() => fetchUserHistory(u.id)}
                                    className={`p-4 rounded-xl border cursor-pointer transition-all flex justify-between items-center ${selectedUser?.id === u.id
                                        ? 'bg-[hsl(var(--primary))]/20 border-[hsl(var(--primary))]'
                                        : 'bg-white/5 border-white/5 hover:border-[hsl(var(--primary))]/50'
                                        }`}
                                >
                                    <div className="flex-1 min-w-0">
                                        <div className="font-bold text-white truncate">{u.full_name || 'Unknown'}</div>
                                        <div className="text-sm text-[hsl(var(--text-muted))] truncate">{u.email}</div>
                                        <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full mt-1 inline-block ${u.role === 'admin' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                                            {u.role}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handleDeleteUser(u.id); }}
                                            className="p-2 hover:bg-red-500/20 text-muted hover:text-red-400 rounded-lg transition-colors"
                                            title="Delete User"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                        <ChevronRight className={`w-4 h-4 transition-transform ${selectedUser?.id === u.id ? 'text-[hsl(var(--primary))] translate-x-1' : 'text-white/20'}`} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Details View */}
                    <div>
                        {selectedUser ? (
                            <div className="space-y-6">
                                <div className="card">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="h3 mb-1">{selectedUser.full_name}'s Profile</h3>
                                            <p className="text-[hsl(var(--text-muted))] text-sm">User ID: {selectedUser.id} • Registered Email: {selectedUser.email}</p>
                                        </div>
                                    </div>
                                </div>

                                <h4 className="text-lg font-bold text-white mb-2 ml-1 flex items-center gap-2">
                                    <Sprout className="w-4 h-4 text-emerald-400" /> Soil Data History
                                </h4>

                                {userHistory.length === 0 ? (
                                    <div className="p-8 text-center border border-dashed border-white/10 rounded-2xl text-[hsl(var(--text-muted))]">
                                        No soil data records found for this user.
                                    </div>
                                ) : (
                                    <div className="grid gap-4">
                                        {userHistory.map((record, i) => (
                                            <div key={i} className="card p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                                                <div>
                                                    <div className="flex items-center gap-2 text-xs text-[hsl(var(--text-muted))] mb-2 uppercase tracking-wide font-bold">
                                                        <Calendar className="w-3 h-3" /> {new Date(record.timestamp).toLocaleDateString()}
                                                        <span className="text-white/20">•</span>
                                                        {new Date(record.timestamp).toLocaleTimeString()}
                                                    </div>
                                                    <div className="flex flex-wrap gap-4">
                                                        <div className="flex flex-col">
                                                            <span className="text-xs text-[hsl(var(--text-muted))]">N</span>
                                                            <span className="text-lg font-bold text-white">{record.n}</span>
                                                        </div>
                                                        <div className="flex flex-col">
                                                            <span className="text-xs text-[hsl(var(--text-muted))]">P</span>
                                                            <span className="text-lg font-bold text-white">{record.p}</span>
                                                        </div>
                                                        <div className="flex flex-col">
                                                            <span className="text-xs text-[hsl(var(--text-muted))]">K</span>
                                                            <span className="text-lg font-bold text-white">{record.k}</span>
                                                        </div>
                                                        <div className="flex flex-col">
                                                            <span className="text-xs text-[hsl(var(--text-muted))]">pH</span>
                                                            <span className="text-lg font-bold text-white">{record.ph}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-[hsl(var(--text-muted))] border-2 border-dashed border-white/5 rounded-3xl p-10">
                                <Users className="w-16 h-16 opacity-20 mb-4" />
                                <p>Select a farmer from the list to view their soil history.</p>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="card p-10 text-center">
                    <PieChart className="w-16 h-16 text-[hsl(var(--primary))] mx-auto mb-4 opacity-50" />
                    <h3 className="h3 mb-2">Advanced Analytics</h3>
                    <p className="text-muted max-w-md mx-auto">This section will contain detailed charts of platform usage, crop recommendations accuracy, and sensor health monitoring.</p>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
