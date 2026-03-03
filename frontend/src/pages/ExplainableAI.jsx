import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';

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
            <div className="container py-10 min-h-screen flex flex-col items-center justify-center text-center">
                <div className="bg-white/5 p-10 rounded-3xl border border-white/10 max-w-md">
                    <Activity className="w-16 h-16 text-[hsl(var(--text-muted))] mx-auto mb-6 opacity-50" />
                    <h2 className="text-2xl font-bold mb-4">No Recent Analysis</h2>
                    <p className="text-[hsl(var(--text-muted))] mb-8">
                        Run a prediction in the <strong>AI Recommendations</strong> section first to see explainable insights here.
                    </p>
                </div>
            </div>
        );
    }

    const { explain, prediction, confidence, type } = analysisData;
    const chartData = explain?.chart_data || [];

    return (
        <div className="container py-10 min-h-screen">
            <h1 className="h2 mb-2">Explainable AI Insights</h1>
            <p className="text-[hsl(var(--text-muted))] mb-8">
                Understanding why the AI recommended <strong>{prediction}</strong>.
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-8">
                {/* Main Chart Card */}
                <div className="card min-h-[500px] flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="h3">Feature Importance (SHAP Values)</h3>
                        <span className="text-xs font-mono bg-white/10 px-2 py-1 rounded text-[hsl(var(--text-muted))]">
                            Model: {type ? type.toUpperCase() : 'UNKNOWN'}
                        </span>
                    </div>

                    <div className="flex-grow w-full min-h-[400px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={chartData}
                                layout="vertical"
                                margin={{ top: 20, right: 30, left: 40, bottom: 20 }}
                            >
                                <XAxis type="number" stroke="hsl(var(--text-muted))" />
                                <YAxis dataKey="name" type="category" width={100} tick={{ fill: 'white', fontSize: 12 }} />
                                <Tooltip
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            const val = payload[0].value;
                                            return (
                                                <div className="glass-panel p-3 border border-white/10 text-sm">
                                                    <p className="font-bold mb-1">{payload[0].payload.name}</p>
                                                    <p className={val > 0 ? "text-emerald-400" : "text-red-400"}>
                                                        Impact: {val > 0 ? '+' : ''}{val}
                                                    </p>
                                                </div>
                                            );
                                        }
                                        return null;
                                    }}
                                />
                                <ReferenceLine x={0} stroke="#666" />
                                <Bar dataKey="impact" barSize={20} radius={[0, 4, 4, 0]}>
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.impact > 0 ? 'hsl(var(--primary))' : '#ef4444'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="text-sm text-[hsl(var(--text-muted))] mt-4 text-center">
                        Positive values (Green) support the decision, while negative values (Red) oppose it.
                    </p>
                </div>

                {/* Key Insights Side Panel */}
                <div className="space-y-6">
                    <div className="card">
                        <h3 className="h3 mb-4">Decision Summary</h3>
                        <div className="space-y-4">
                            <div className="p-4 rounded-xl bg-[hsl(var(--primary))]/10 border border-[hsl(var(--primary))]/20">
                                <div className="text-xs text-[hsl(var(--primary))] font-bold uppercase tracking-wider mb-1">Recommendation</div>
                                <div className="text-2xl font-bold text-white">{prediction}</div>
                                {confidence && <div className="text-sm text-[hsl(var(--primary))] opacity-80">{(confidence * 100).toFixed(1)}% Confidence</div>}
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <h3 className="h3 mb-4">Top Influencers</h3>
                        <div className="space-y-3">
                            {chartData
                                .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
                                .slice(0, 3)
                                .map((factor, i) => (
                                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                                        {factor.impact > 0 ? (
                                            <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5" />
                                        ) : (
                                            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" />
                                        )}
                                        <div>
                                            <div className="font-bold text-white text-sm">{factor.name}</div>
                                            <div className="text-xs text-[hsl(var(--text-muted))]">
                                                {factor.impact > 0 ? "Strongly supports this outcome" : "Reduced the confidence score"}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            }
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExplainableAI;
