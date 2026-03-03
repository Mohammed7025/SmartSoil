import React, { useState, useEffect } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { Leaf, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: 'Home', to: '/' },
        { name: 'Dashboard', to: '/dashboard' },
        { name: 'Advisor', to: '/advisor' },
        { name: 'Tools', to: '/tools' },
    ];

    return (
        <nav
            className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${isScrolled || location.pathname !== '/' ? 'bg-[rgba(10,15,30,0.8)] backdrop-blur-md border-b border-[var(--glass-border)]' : 'bg-transparent'
                }`}
        >
            <div className="container flex items-center justify-between h-20">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 cursor-pointer group">
                    <div className="p-2 bg-[rgba(0,255,118,0.1)] rounded-full group-hover:bg-[hsl(var(--primary))] transition-colors">
                        <Leaf className="w-6 h-6 text-[hsl(var(--primary))] group-hover:text-black transition-colors" />
                    </div>
                    <span className="text-xl font-bold tracking-tight group-hover:text-white transition-colors">Smart Soil</span>
                </Link>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-8">
                    {navLinks.map((link) => (
                        <NavLink
                            key={link.name}
                            to={link.to}
                            className={({ isActive }) =>
                                `text-sm font-medium transition-all duration-300 relative py-2 ${isActive ? 'text-[hsl(var(--primary))]' : 'text-[hsl(var(--text-secondary))] hover:text-white'
                                }`
                            }
                        >
                            {({ isActive }) => (
                                <>
                                    {link.name}
                                    {isActive && (
                                        <motion.div
                                            layoutId="nav-pill"
                                            className="absolute bottom-0 left-0 w-full h-[2px] bg-[hsl(var(--primary))] rounded-full"
                                        />
                                    )}
                                </>
                            )}
                        </NavLink>
                    ))}
                    <button className="btn btn-primary py-2 px-6 text-sm shadow-[0_0_20px_rgba(0,230,118,0.3)] hover:shadow-[0_0_30px_rgba(0,230,118,0.5)]">Sign In</button>
                </div>

                {/* Mobile Menu Toggle */}
                <div className="md:hidden">
                    <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-[hsl(var(--text-primary))]">
                        {isMobileMenuOpen ? <X /> : <Menu />}
                    </button>
                </div>
            </div>

            {/* Mobile Nav */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="md:hidden bg-[hsl(var(--bg-card))] border-b border-[var(--glass-border)] overflow-hidden"
                    >
                        <div className="flex flex-col p-4 gap-4">
                            {navLinks.map((link) => (
                                <NavLink
                                    key={link.name}
                                    to={link.to}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        `text-base font-medium ${isActive ? 'text-[hsl(var(--primary))]' : 'text-[hsl(var(--text-secondary))]'}`
                                    }
                                >
                                    {link.name}
                                </NavLink>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};
export default Navbar;
