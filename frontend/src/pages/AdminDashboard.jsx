import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Users, Sprout, Calendar, ChevronRight } from 'lucide-react';

const AdminDashboard = () => {
    const { currentUser } = useAuth();
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [userHistory, setUserHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simple role check
        if (!currentUser || currentUser.role !== 'admin') {
            navigate('/dashboard'); // or unauthorized page
            return;
        }
        fetchUsers();
    }, [currentUser, navigate]);

    const fetchUsers = async () => {
        try {
            const res = await fetch('http://localhost:8000/admin/users');
            if (res.ok) {
                const data = await res.json();
                setUsers(data);
            }
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchUserHistory = async (userId) => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/admin/users/${userId}/history`);
            if (res.ok) {
                const data = await res.json();
                setSelectedUser(data.user);
                setUserHistory(data.history);
            }
        } catch (error) {
            console.error("Failed to fetch history", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading && !users.length) return <div className="p-10 text-center text-white">Loading Admin Panel...</div>;

    return (
        <div className="container py-10 min-h-screen">
            <h1 className="h2 mb-2">Admin Dashboard</h1>
            <p className="text-muted mb-8">Manage users and view agricultural data.</p>

            <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-8">

                {/* User List */}
                <div className="card h-fit">
                    <h3 className="h3 mb-4 flex items-center gap-2">
                        <Users className="w-5 h-5 text-[hsl(var(--primary))]" /> Registered Farmers
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
                                <div>
                                    <div className="font-bold text-white">{u.full_name || 'Unknown'}</div>
                                    <div className="text-sm text-[hsl(var(--text-muted))]">{u.email}</div>
                                </div>
                                <ChevronRight className={`w-4 h-4 transition-transform ${selectedUser?.id === u.id ? 'text-[hsl(var(--primary))] translate-x-1' : 'text-white/20'}`} />
                            </div>
                        ))}
                    </div>
                </div>

                {/* Details View */}
                <div>
                    {selectedUser ? (
                        <div className="space-y-6">
                            <div className="card">
                                <h3 className="h3 mb-1">{selectedUser.full_name}'s Profile</h3>
                                <p className="text-[hsl(var(--text-muted))] text-sm">User ID: {selectedUser.id} • Role: {selectedUser.role}</p>
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
                                                        <span className="text-xs text-[hsl(var(--text-muted))]">Nitrogen</span>
                                                        <span className="text-lg font-bold text-white">{record.n}</span>
                                                    </div>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs text-[hsl(var(--text-muted))]">Phosphorus</span>
                                                        <span className="text-lg font-bold text-white">{record.p}</span>
                                                    </div>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs text-[hsl(var(--text-muted))]">Potassium</span>
                                                        <span className="text-lg font-bold text-white">{record.k}</span>
                                                    </div>
                                                    <div className="flex flex-col">
                                                        <span className="text-xs text-[hsl(var(--text-muted))]">pH Level</span>
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
                        <div className="h-full flex flex-col items-center justify-center text-[hsl(var(--text-muted))] border-2 border-dashed border-white/5 rounded-3xl p-10">
                            <Users className="w-16 h-16 opacity-20 mb-4" />
                            <p>Select a farmer from the list to view their details.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
