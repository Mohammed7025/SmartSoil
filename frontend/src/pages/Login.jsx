import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Leaf, Lock, Mail } from 'lucide-react';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const successMessage = location.state?.message;

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setError('');
            setLoading(true);
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            console.error(err);
            setError('Failed to log in: ' + err.message);
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#F5F1E8] p-6">
            <div className="card w-full max-w-[420px] !p-10">
                <div className="text-center mb-8">
                    <div className="w-14 h-14 bg-[#7C6F64] text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-[#7C6F64]/20">
                        <Leaf size={32} />
                    </div>
                    <h1 className="h2 mb-2">Welcome Back</h1>
                    <p className="text-[#6B6259]">Sign in to your Smart Soil account</p>
                </div>

                {successMessage && (
                    <div style={{
                        backgroundColor: 'hsl(var(--primary) / 0.1)',
                        color: 'hsl(var(--primary))',
                        padding: '0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        marginBottom: '1.5rem',
                        fontSize: '0.875rem'
                    }}>
                        {successMessage}
                    </div>
                )}

                {error && (
                    <div style={{
                        backgroundColor: 'hsl(var(--accent) / 0.1)',
                        color: 'hsl(var(--accent))',
                        padding: '0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        marginBottom: '1.5rem',
                        fontSize: '0.875rem'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-[#6B6259] mb-2 ml-1">Email Address</label>
                        <div className="relative">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#9C8F80]">
                                <Mail size={18} />
                            </div>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full !pl-12 !py-4"
                                placeholder="admin@smartsoil.com"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest text-[#6B6259] mb-2 ml-1">Password</label>
                        <div className="relative">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#9C8F80]">
                                <Lock size={18} />
                            </div>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full !pl-12 !py-4"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn btn-primary w-full justify-center !py-4 mt-4 shadow-lg shadow-[#7C6F64]/20"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>

                    <div className="text-center pt-4">
                        <p className="text-[#6B6259] text-sm">
                            Don't have an account? <Link to="/signup" className="text-[#7C6F64] font-bold hover:underline">Create Account</Link>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;
