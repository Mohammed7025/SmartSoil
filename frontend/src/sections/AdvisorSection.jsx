import React, { useState } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AdvisorSection = () => {
    const [messages, setMessages] = useState([
        { id: 1, role: 'bot', text: 'Hello! I am your Smart Soil AI Advisor. Ask me anything about your crops, soil conditions, or farming tips.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add User Message
        const userMsg = { id: Date.now(), role: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        // Call Backend API
        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input, context: "User is on the web interface." })
            });

            const data = await response.json();

            if (response.ok) {
                const botMsg = { id: Date.now() + 1, role: 'bot', text: data.response };
                setMessages(prev => [...prev, botMsg]);
            } else {
                throw new Error(data.detail || "Failed to get response");
            }
        } catch (error) {
            console.error("Chat Error:", error);
            const errorMsg = { id: Date.now() + 1, role: 'bot', text: "Sorry, I'm having trouble connecting to the AI brain right now. Please try again later." };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section id="advisor" className="min-h-screen py-8 relative">
            {/* Background Glow */}
            <div className="absolute right-0 top-1/4 w-96 h-96 bg-[hsl(var(--primary))] opacity-10 rounded-full blur-[100px] z-[-1]" />

            <div className="container h-[calc(100vh-140px)]">
                {/* Desktop Layout: Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6 h-full">

                    {/* Left Sidebar (Desktop Only) */}
                    <div className="hidden lg:flex flex-col gap-4">
                        <div className="glass-panel p-6 flex-1 flex flex-col">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 bg-[hsl(var(--primary))] rounded-lg">
                                    <Bot className="w-6 h-6 text-black" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg">AI Advisor</h3>
                                    <span className="text-xs text-[hsl(var(--text-muted))] flex items-center gap-1">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /> Online
                                    </span>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-[hsl(var(--text-secondary))] mb-2">Suggested Topics</h4>
                                {['Crop Disease', 'Irrigation Tips', 'Soil pH Levels', 'Fertilizer Guide'].map((topic) => (
                                    <button
                                        key={topic}
                                        onClick={() => setInput(topic)}
                                        className="w-full text-left px-4 py-3 rounded-xl bg-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.08)] transition-colors text-sm"
                                    >
                                        {topic}
                                    </button>
                                ))}
                            </div>

                            <div className="mt-auto pt-6 border-t border-[var(--glass-border)]">
                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[rgba(255,191,0,0.1)] border border-[rgba(255,191,0,0.2)]">
                                    <Sparkles className="w-3 h-3 text-[hsl(var(--accent))]" />
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[hsl(var(--accent))]">Gemini Pro Model</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Chat Area */}
                    <div className="glass-panel flex flex-col overflow-hidden h-full relative">
                        {/* Mobile Header (Hidden on Desktop) */}
                        <div className="lg:hidden p-4 border-b border-[var(--glass-border)] flex items-center gap-2">
                            <Bot className="w-6 h-6 text-[hsl(var(--primary))]" />
                            <span className="font-bold">Smart Soil AI</span>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6">
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    {msg.role === 'bot' && (
                                        <div className="w-10 h-10 rounded-full bg-[rgba(0,230,118,0.1)] border border-[hsl(var(--primary))] flex items-center justify-center flex-shrink-0">
                                            <Bot className="w-5 h-5 text-[hsl(var(--primary))]" />
                                        </div>
                                    )}

                                    <div className={`max-w-[75%] p-5 rounded-2xl shadow-sm ${msg.role === 'user'
                                        ? 'bg-[hsl(var(--primary))] text-black rounded-tr-none'
                                        : 'bg-[rgba(255,255,255,0.03)] border border-[var(--glass-border)] rounded-tl-none'
                                        }`}>
                                        <p className="text-base leading-relaxed">{msg.text}</p>
                                    </div>

                                    {msg.role === 'user' && (
                                        <div className="w-10 h-10 rounded-full bg-[rgba(255,255,255,0.1)] flex items-center justify-center flex-shrink-0">
                                            <User className="w-5 h-5" />
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                            {isLoading && (
                                <div className="flex gap-4">
                                    <div className="w-10 h-10 rounded-full bg-[rgba(0,230,118,0.1)] border border-[hsl(var(--primary))] flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-[hsl(var(--primary))]" />
                                    </div>
                                    <div className="bg-[rgba(255,255,255,0.03)] p-5 rounded-2xl rounded-tl-none flex items-center gap-2 border border-[var(--glass-border)]">
                                        <span className="w-2 h-2 bg-[hsl(var(--text-muted))] rounded-full animate-bounce" />
                                        <span className="w-2 h-2 bg-[hsl(var(--text-muted))] rounded-full animate-bounce delay-100" />
                                        <span className="w-2 h-2 bg-[hsl(var(--text-muted))] rounded-full animate-bounce delay-200" />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Area */}
                        <div className="p-6 border-t border-[var(--glass-border)] bg-[rgba(0,0,0,0.2)]">
                            <div className="flex gap-4">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Type your question here..."
                                    className="flex-1 bg-[hsl(var(--bg-input))] border border-[var(--glass-border)] rounded-xl px-6 py-4 text-[hsl(var(--text-primary))] focus:outline-none focus:border-[hsl(var(--primary))] focus:ring-1 focus:ring-[hsl(var(--primary))] transition-all shadow-inner"
                                    disabled={isLoading}
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={isLoading}
                                    className="btn btn-primary px-8 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-[0_0_20px_rgba(0,230,118,0.4)]"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default AdvisorSection;
