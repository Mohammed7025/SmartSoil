import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const AdvisorSection = () => {
    const [messages, setMessages] = useState([
        { id: 1, role: 'bot', text: "Hello. I'm AgroBot. How can I help you with your farming today?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({
                top: scrollRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, [messages, isLoading]);

    const handleSend = async (overrideInput) => {
        const messageText = overrideInput || input;
        if (!messageText.trim()) return;

        // User message
        const userMsg = { id: Date.now(), role: 'user', text: messageText };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    user_id: "web_user_123",
                    context: "User is on the web interface with streaming support."
                })
            });

            if (!response.ok) throw new Error("Failed to connect");

            // Initialize Bot Message in state
            const botMsgId = Date.now() + 1;
            setMessages(prev => [...prev, { id: botMsgId, role: 'bot', text: '' }]);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                if (!chunk) continue;
                accumulatedText += chunk;

                // Update the specifically created bot message
                setMessages(prev => prev.map(m =>
                    m.id === botMsgId ? { ...m, text: accumulatedText } : m
                ));
            }

            // Final flush of decoder
            const lastChunk = decoder.decode();
            if (lastChunk) {
                accumulatedText += lastChunk;
                setMessages(prev => prev.map(m =>
                    m.id === botMsgId ? { ...m, text: accumulatedText } : m
                ));
            }

        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [...prev, { id: Date.now() + 2, role: 'bot', text: "I'm having trouble connecting. Please try again soon." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <section className="min-h-screen py-16 px-4 bg-[hsl(var(--off-white))] font-['Poppins',_sans-serif]">
            <div className="max-w-2xl mx-auto">
                <div className="bg-white rounded-[40px] shadow-2xl overflow-hidden border border-[hsla(var(--earth-brown),0.1)] flex flex-col h-[700px] wood-texture relative">

                    {/* Header: Minimal & Professional */}
                    <div className="pt-10 pb-6 text-center border-b border-[hsla(var(--earth-brown),0.05)] bg-white/40 backdrop-blur-md">
                        <h1 className="text-2xl font-semibold text-[hsl(var(--earth-brown))] tracking-wide">
                            AgroBot
                        </h1>
                    </div>

                    {/* Chat Area */}
                    <div
                        ref={scrollRef}
                        className="flex-1 overflow-y-auto p-8 space-y-6 no-scrollbar"
                    >
                        <AnimatePresence initial={false}>
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 15, scale: 0.98 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    transition={{ duration: 0.5, ease: "easeOut" }}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[70%] px-[16px] py-[12px] rounded-[18px] text-[15px] leading-[1.5] shadow-sm ${msg.role === 'user'
                                            ? 'bg-[hsl(var(--earth-brown))] text-white rounded-tr-none'
                                            : 'bg-[hsl(var(--agrobot-cream))] text-[hsl(var(--earth-brown))] border border-[hsla(var(--earth-brown),0.05)] rounded-tl-none'
                                            }`}
                                    >
                                        {msg.text}
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {isLoading && messages[messages.length - 1]?.role !== 'bot' && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex justify-start"
                            >
                                <div className="bg-[hsl(var(--agrobot-cream))] px-5 py-4 rounded-[18px] rounded-tl-none border border-[hsla(var(--earth-brown),0.05)]">
                                    <div className="flex gap-1.5 items-center">
                                        <div className="w-1.5 h-1.5 bg-[hsl(var(--earth-brown))] rounded-full animate-bounce [animation-delay:-0.3s]" />
                                        <div className="w-1.5 h-1.5 bg-[hsl(var(--earth-brown))] rounded-full animate-bounce [animation-delay:-0.15s]" />
                                        <div className="w-1.5 h-1.5 bg-[hsl(var(--earth-brown))] rounded-full animate-bounce" />
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </div>

                    {/* Quick Suggestion Buttons */}
                    <div className="px-8 py-3 flex gap-2.5 overflow-x-auto no-scrollbar justify-center">
                        {['Crop Advice', 'Soil Health', 'Irrigation', 'Fertilizer Guidance'].map((option) => (
                            <button
                                key={option}
                                onClick={() => handleSend(option)}
                                className="whitespace-nowrap px-5 py-2.5 rounded-full border border-[hsla(var(--earth-brown),0.15)] text-[hsl(var(--earth-brown))] text-xs font-semibold hover:bg-[hsl(var(--earth-brown))] hover:text-white transition-all duration-300 active:scale-95"
                            >
                                {option}
                            </button>
                        ))}
                    </div>

                    {/* Input Area */}
                    <div className="p-8 bg-white/40 backdrop-blur-md border-t border-[hsla(var(--earth-brown),0.05)]">
                        <div className="flex items-center gap-3">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                                placeholder={isLoading ? "AgroBot is typing..." : "How can I help you today?"}
                                disabled={isLoading}
                                className="flex-1 bg-white/80 border border-[hsla(var(--earth-brown),0.1)] rounded-[20px] px-6 py-4 text-sm focus:outline-none focus:ring-1 focus:ring-[hsl(var(--earth-brown))] placeholder:text-[hsla(var(--earth-brown),0.3)] text-[hsl(var(--earth-brown))] transition-all shadow-inner disabled:opacity-50"
                            />
                            <button
                                onClick={() => handleSend()}
                                disabled={isLoading}
                                className="px-7 py-4 bg-[hsl(var(--earth-brown))] text-white rounded-[20px] text-sm font-semibold hover:opacity-90 active:scale-95 transition-all shadow-md disabled:opacity-50 disabled:scale-100"
                            >
                                {isLoading ? "..." : "Send"}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default AdvisorSection;
