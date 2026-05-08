import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';
import { Activity, AlertTriangle, CheckCircle, Brain, Target, Info, ArrowLeft, Layers, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const ExplainableAI = () => {
    const [analysisData, setAnalysisData] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem('latestAnalysis');
        if (stored) {
            setAnalysisData(JSON.parse(stored));
        }
    }, []);

    if (!analysisData) {
        return (
            <div className="container py-20 min-h-screen flex flex-col items-center justify-center text-center">
                <div className="bg-white p-10 rounded-2xl border border-slate-200 shadow-sm max-w-md">
                    <Brain className="w-12 h-12 text-primary mx-auto mb-6" />
                    <h2 className="text-2xl font-bold mb-4">No Recent Analysis</h2>
                    <p className="text-slate-600 mb-8">
                        The AI needs recent analysis data to provide insights. Run a prediction in the Hub first.
                    </p>
                    <Link to="/" className="btn btn-primary px-8 py-3 rounded-lg">
                        Go to Hub
                    </Link>
                </div>
            </div>
        );
    }

    const { explain, prediction, nutrient_data, type, status } = analysisData;
    const isCrop = type === 'crop';
    const isIrrigation = type === 'irrigation';
    const useShapChart = isCrop || isIrrigation;
    const displayResult = isIrrigation ? status : prediction;
    const chartData = explain?.chart_data || [];

    // --- Insight Generator ---
    const generateInsight = () => {
        if (!useShapChart) {
            const lowNutrients = nutrient_data?.filter(n => n.status === "Low").map(n => n.name.toLowerCase());
            if (lowNutrients && lowNutrients.length > 0) {
                return `Current ${lowNutrients.join(" and ")} levels are below optimal range, so ${displayResult} is recommended to restore your soil's health.`;
            }
            return `Nutrient levels are within a moderate range. ${displayResult} will help maintain optimal fertility for your next planting cycle.`;
        }

        // Find top contributing factors
        const sorted = [...chartData].sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
        const top = sorted[0];
        if (!top) return `The AI identified ${displayResult} as the best choice for your current soil and environmental conditions.`;

        const intensity = Math.abs(top.impact) > 5 ? "strongly supports" : "supports";
        const direction = top.impact > 0 ? intensity : "slightly reduces the suitability of other options, favoring";

        return `${top.name} levels ${direction} ${displayResult} ${isIrrigation ? 'irrigation requirement' : 'growth'} in your current climate.`;
    };

    return (
        <div className="min-h-screen pb-20 bg-slate-50 font-sans">
            <div className="container py-10">
                {/* Header */}
                <div className="mb-10">
                    <Link to="/" className="inline-flex items-center text-sm font-bold text-primary hover:text-primary-light mb-4 group transition-colors">
                        <ArrowLeft className="w-4 h-4 mr-1" />
                        Back to Hub
                    </Link>
                    <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight leading-none mb-3">
                        {isCrop ? "Why this Crop?" : isIrrigation ? "Watering Factors" : "Soil Nutrient Dashboard"}
                    </h1>
                    <p className="text-slate-500 text-lg">
                        Professional AI Analysis for <span className="text-slate-900 font-bold">{displayResult || 'the latest prediction'}</span>
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left: Visualization */}
                    <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 shadow-sm p-8 min-h-[500px] flex flex-col">
                        <div className="flex items-center justify-between mb-8 border-b border-slate-100 pb-6">
                            <h3 className="text-xl font-bold text-slate-900">
                                {useShapChart ? "AI Decision Factors (SHAP)" : "Nutrient Levels (Current vs Ideal)"}
                            </h3>
                            <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-[10px] font-black uppercase tracking-wider">
                                {useShapChart ? "SHAP ANALYSIS" : "SOIL DEFICIENCY"}
                            </span>
                        </div>

                        <div className="flex-grow w-full">
                            {useShapChart ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                        <XAxis type="number" stroke="#94a3b8" fontSize={12} />
                                        <YAxis dataKey="name" type="category" width={110} tick={{ fill: '#475569', fontSize: 13, fontWeight: 700 }} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            cursor={{ fill: '#f8fafc' }}
                                            content={({ active, payload }) => {
                                                if (!active || !payload) return null;
                                                const val = payload[0].value;
                                                return (
                                                    <div className="bg-white px-4 py-3 border border-slate-200 rounded-lg shadow-lg">
                                                        <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">{payload[0].payload.name}</div>
                                                        <div className={`text-xl font-black ${val > 0 ? "text-emerald-600" : "text-red-500"}`}>
                                                            {val > 0 ? '+' : ''}{val}
                                                        </div>
                                                        <div className="text-[10px] text-slate-500">Feature Impact</div>
                                                    </div>
                                                );
                                            }}
                                        />
                                        <Bar dataKey="impact" barSize={32} radius={[0, 4, 4, 0]}>
                                            {chartData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.impact > 0 ? '#10b981' : '#ef4444'} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={nutrient_data} layout="vertical" margin={{ top: 20, right: 40, left: 20, bottom: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                        <XAxis type="number" stroke="#94a3b8" fontSize={12} />
                                        <YAxis dataKey="name" type="category" width={110} tick={{ fill: '#475569', fontSize: 13, fontWeight: 700 }} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            cursor={{ fill: '#f8fafc' }}
                                            content={({ active, payload }) => {
                                                if (!active || !payload) return null;
                                                const { current, ideal, status } = payload[0].payload;
                                                return (
                                                    <div className="bg-white px-4 py-3 border border-slate-200 rounded-lg shadow-lg">
                                                        <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">{payload[0].payload.name}</div>
                                                        <div className="text-lg font-black text-slate-900">{current} / {ideal}</div>
                                                        <div className={`text-[10px] font-bold uppercase ${status === 'Low' ? 'text-red-500' : 'text-emerald-600'}`}>Status: {status}</div>
                                                    </div>
                                                );
                                            }}
                                        />
                                        <Bar dataKey="current" barSize={32} radius={[0, 4, 4, 0]}>
                                            {nutrient_data?.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.status === 'Low' ? '#ef4444' : entry.status === 'Moderate' ? '#f59e0b' : '#10b981'} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            )}
                        </div>

                        {/* Chart Legend */}
                        <div className="mt-8 flex items-center gap-8 border-t border-slate-50 pt-8">
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 rounded-sm bg-emerald-500" />
                                <span className="text-xs text-slate-600 font-medium">{useShapChart ? "Supports Result" : "Optimal Range"}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 rounded-sm bg-red-500" />
                                <span className="text-xs text-slate-600 font-medium">{useShapChart ? "Reduces Result" : "Deficient / Low"}</span>
                            </div>
                            {!useShapChart && (
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-4 rounded-sm bg-amber-500" />
                                    <span className="text-xs text-slate-600 font-medium">Moderate Level</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Decision Panel */}
                    <div className="space-y-8">
                        {/* Final Recommendation Card */}
                        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
                                <Sparkles size={16} className="text-primary" /> Recommended Result
                            </h3>
                            <div className="p-6 rounded-2xl bg-primary/5 border border-primary/10 text-center">
                                <div className="text-4xl font-black text-primary tracking-tight">
                                    {displayResult || (isIrrigation ? "Moisture Analysis" : 'N/A')}
                                </div>
                            </div>
                        </div>

                        {/* Analysis Card */}
                        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8">
                            <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
                                <Brain size={16} className="text-primary" /> Expert Analysis
                            </h3>
                            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                                <p className="text-sm text-slate-700 leading-relaxed font-medium">
                                    {generateInsight()}
                                </p>
                            </div>

                            {/* Top Drivers for SHAP only */}
                            {useShapChart && chartData.length > 0 && (
                                <div className="mt-8 space-y-4">
                                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Top Drivers</div>
                                    {chartData
                                        .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
                                        .slice(0, 2)
                                        .map((factor, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                                                <span className="text-xs font-bold text-slate-700">{factor.name}</span>
                                                <span className={`text-[10px] font-black ${factor.impact > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                                                    {factor.impact > 0 ? "STRENGTH" : "LIMITATION"}
                                                </span>
                                            </div>
                                        ))
                                    }
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExplainableAI;
