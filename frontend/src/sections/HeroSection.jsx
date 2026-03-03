import React from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, Leaf, Activity, MessageSquare } from 'lucide-react';
import { Link } from 'react-scroll';

const HeroSection = () => {
    return (
        <section id="hero" className="min-h-screen relative flex items-center justify-center overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[hsl(var(--bg-dark))] z-0" />
            <div className="absolute top-0 left-0 w-full h-full opacity-30 z-[-1]">
                {/* Abstract Green Glows */}
                <div className="absolute top-10 left-1/4 w-96 h-96 bg-[hsl(var(--primary))] rounded-full blur-[128px]" />
                <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-[hsl(var(--secondary))] rounded-full blur-[128px]" />
            </div>

            <div className="container relative z-10 text-center px-4">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel mb-6">
                        <Leaf className="w-5 h-5 text-[hsl(var(--primary))]" />
                        <span className="text-sm font-medium tracking-wide uppercase text-[hsl(var(--text-secondary))]">
                            AI Powered Agriculture
                        </span>
                    </div>

                    <h1 className="text-6xl md:text-8xl font-bold mb-6 tracking-tight">
                        Smart <span className="text-gradient">Soil</span>
                    </h1>

                    <p className="text-xl md:text-2xl text-[hsl(var(--text-muted))] max-w-2xl mx-auto mb-10 leading-relaxed">
                        Real-time monitoring and intelligent crop insights at your fingertips.
                    </p>

                    <div className="flex flex-col md:flex-row items-center justify-center gap-4">
                        <Link to="dashboard" smooth={true} duration={500} offset={-50}>
                            <button className="btn btn-primary gap-2">
                                <Activity className="w-5 h-5" />
                                Live Dashboard
                            </button>
                        </Link>
                        <Link to="advisor" smooth={true} duration={500} offset={-50}>
                            <button className="btn btn-ghost gap-2">
                                <MessageSquare className="w-5 h-5" />
                                AI Advisor
                            </button>
                        </Link>
                    </div>
                </motion.div>
            </div>

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1, duration: 1 }}
                className="absolute bottom-10 left-1/2 -translate-x-1/2 text-[hsl(var(--text-muted))]"
            >
                <ChevronDown className="w-6 h-6 animate-bounce" />
            </motion.div>
        </section>
    );
};

export default HeroSection;
