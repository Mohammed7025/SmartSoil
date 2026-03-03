import React, { useState } from 'react';
import { getCurrentWeather, getLatestSoilData } from '../services/api';
import { Sprout, Beaker, ChevronRight, Activity, Sparkles, Wind, Droplets, Thermometer, Database, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

const ToolCard = ({ title, desc, icon: Icon, onClick }) => (
    <motion.div
        whileHover={{ y: -5, scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
        className="glass-panel p-8 cursor-pointer group relative overflow-hidden border border-white/5 hover:border-[hsl(var(--primary))] transition-all duration-300 shadow-2xl hover:shadow-[0_0_30px_rgba(0,230,118,0.1)]"
    >
        <div className="absolute top-0 right-0 w-32 h-32 bg-[hsl(var(--primary))] opacity-5 rounded-full blur-[50px] -mr-16 -mt-16 group-hover:opacity-10 transition-opacity" />

        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[rgba(0,204,106,0.2)] to-[rgba(0,204,106,0.05)] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 border border-white/5">
            <Icon className="w-8 h-8 text-emerald-400 group-hover:text-white transition-colors" />
        </div>

        <h3 className="text-2xl font-bold mb-3 text-white group-hover:text-emerald-400 transition-colors">{title}</h3>
        <p className="text-gray-300 mb-8 leading-relaxed">{desc}</p>

        <div className="flex items-center text-emerald-400 font-bold text-sm uppercase tracking-wide">
            Launch Tool <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
        </div>
    </motion.div>
);

const InputField = ({ label, name, value, onChange, placeholder, icon: Icon }) => (
    <div className="group">
        <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[hsl(var(--text-secondary))] mb-2 ml-1 group-focus-within:text-[hsl(var(--primary))] transition-colors">
            {Icon && <Icon className="w-3 h-3" />} {label}
        </label>
        <div className="relative">
            <input
                type="number"
                name={name}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="w-full bg-[rgba(0,0,0,0.2)] border border-white/10 rounded-xl px-4 py-4 text-white placeholder-white/20 focus:border-[hsl(var(--primary))] focus:bg-[rgba(0,230,118,0.05)] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] transition-all font-medium"
            />
        </div>
    </div>
);

const RecommendationSection = () => {
    const [activeTool, setActiveTool] = useState(null);
    const [formData, setFormData] = useState({
        n: '', p: '', k: '',
        temperature: '', humidity: '', ph: '', rainfall: ''
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Expert Advice Data
    const FERTILIZER_INFO = {
        'Urea': { type: 'Nitrogen Source (46% N)', tip: 'Promotes rapid vegetative growth. Apply in split doses to minimize leaching.' },
        'DAP': { type: 'Phosphorus Source (18-46-0)', tip: 'Crucial for root development and crop establishment. Best applied as a basal dose.' },
        '28-28': { type: 'High Nitrogen-Phosphorus', tip: 'Balances vegetative and root growth. Ideal for early crop stages.' },
        '14-35-14': { type: 'High Phosphorus', tip: 'Supports vigorous rooting and flowering. Apply near the root zone.' },
        '17-17-17': { type: 'Balanced NPK', tip: 'All-purpose nutrition for maintaining plant health throughout the season.' },
        '20-20': { type: 'Balanced Nitrogen-Phosphorus', tip: 'Boosts early growth. Ensure adequate potassium is also available.' },
        '10-26-26': { type: 'High P-K Complex', tip: 'Excellent for flowering, fruiting, and grain filling stages. Improves quality.' }
    };

    const getIrrigationTip = (hours, temp) => {
        if (hours <= 0) return "Soil moisture is sufficient. Conserve water.";
        if (temp > 30) return "High heat detected. Water in the early morning (4-6 AM) to reduce evaporation loss.";
        return "Watering recommended. Ensure even field coverage to prevent waterlogging.";
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handlePredict = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        // API Endpoint Logic (Matching Flutter App)
        let endpoint = 'http://localhost:8000/predict';
        if (activeTool === 'crop') endpoint += '/crop';
        else if (activeTool === 'fertilizer') endpoint += '/fertilizer';
        else if (activeTool === 'irrigation') endpoint += '/irrigation';

        try {
            // Strict Float Parsing (Matching Flutter Logic)
            const payload = {
                n: parseFloat(formData.n) || 0.0,
                p: parseFloat(formData.p) || 0.0,
                k: parseFloat(formData.k) || 0.0,
                temperature: parseFloat(formData.temperature) || 0.0,
                humidity: parseFloat(formData.humidity) || 0.0,
                ph: parseFloat(formData.ph) || 7.0, // Default pH 7
                rainfall: parseFloat(formData.rainfall) || 0.0
            };

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);

            const data = await response.json();

            // Save for Explainable AI Page
            localStorage.setItem('latestAnalysis', JSON.stringify({
                type: activeTool,
                ...data
            }));

            setTimeout(() => {
                setResult(data);
                setLoading(false);
            }, 500);

        } catch (err) {
            console.error(err);
            setError("Failed to connect to AI Backend.");
            setLoading(false);
        }
    };

    const handleFetchWeather = async () => {
        try {
            const data = await getCurrentWeather();

            // Allow manual override if needed, but fill with API data
            // Use forecast rain if current rain is 0, to give some data
            const rainValue = data.rainfall > 0 ? data.rainfall : (data.rainfall_forecast_24h || 0);

            setFormData(prev => ({
                ...prev,
                temperature: data.temperature || prev.temperature,
                humidity: data.humidity || prev.humidity,
                rainfall: rainValue || prev.rainfall
            }));
        } catch (e) {
            console.error(e);
            alert("Error connecting to weather service. Please check your internet or backend connection.");
        }
    };

    const handleFetchSoilData = async () => {
        try {
            const data = await getLatestSoilData();
            if (data) {
                setFormData(prev => ({
                    ...prev,
                    n: data.n || prev.n,
                    p: data.p || prev.p,
                    k: data.k || prev.k,
                    ph: data.ph || prev.ph,
                    // Some sensors might also provide humidity/temp
                    humidity: data.moisture || prev.humidity
                }));
            } else {
                alert("No live soil data available.");
            }
        } catch (e) {
            console.error(e);
            alert("Error fetching live soil data.");
        }
    };

    const resetForm = () => {
        setFormData({ n: '', p: '', k: '', temperature: '', humidity: '', ph: '', rainfall: '' });
        setResult(null);
        setError(null);
    };

    return (
        <section id="tools" className="relative py-20 min-h-screen overflow-hidden">
            {/* Ambient Background Elements */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-[#051005] to-black/90 pointer-events-none" />
            <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[hsl(var(--primary))] opacity-[0.03] rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-blue-500 opacity-[0.02] rounded-full blur-[120px] pointer-events-none" />

            <div className="container relative z-10 px-4 md:px-6">
                <AnimatePresence mode="wait">
                    {!activeTool ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="max-w-6xl mx-auto pt-10"
                        >
                            <div className="mb-20 text-center">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.6 }}
                                >
                                    <h2 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight text-white">
                                        AI <span className="text-transparent bg-clip-text bg-gradient-to-r from-[hsl(var(--primary))] to-emerald-300">Analysis</span>
                                    </h2>
                                    <p className="text-xl text-[hsl(var(--text-muted))] max-w-2xl mx-auto leading-relaxed">
                                        Precision agriculture powered by advanced machine learning models. Select a tool to begin optimizing your yield.
                                    </p>
                                </motion.div>
                            </div>

                            <motion.div
                                initial={{ opacity: 0, y: 40 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: 0.2 }}
                                className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12"
                            >
                                <ToolCard
                                    title="Crop Recommender"
                                    desc="Our flagship model analyzes 7 distinct soil and climate parameters to predict the optimal crop with 98% accuracy."
                                    icon={Sprout}
                                    onClick={() => setActiveTool('crop')}
                                />
                                <ToolCard
                                    title="Fertilizer Optimizer"
                                    desc="Calculate exact nutrient deficiencies and get precise N-P-K chemical dosage recommendations for your soil."
                                    icon={Beaker}
                                    onClick={() => setActiveTool('fertilizer')}
                                />
                                <ToolCard
                                    title="Irrigation Scheduler"
                                    desc="AI-driven water management calculator. Predicts precise irrigation hours based on soil moisture and rainfall."
                                    icon={Droplets}
                                    onClick={() => setActiveTool('irrigation')}
                                />
                            </motion.div>
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.4 }}
                            className="h-full"
                        >
                            <button
                                onClick={() => { setActiveTool(null); resetForm(); }}
                                className="group mb-8 flex items-center gap-3 px-5 py-2.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 hover:border-[hsl(var(--primary))] transition-all text-sm font-medium text-[hsl(var(--text-muted))] hover:text-white"
                            >
                                <ChevronRight className="w-4 h-4 rotate-180 group-hover:-translate-x-1 transition-transform" />
                                Return to Hub
                            </button>

                            <div className="grid grid-cols-1 lg:grid-cols-[1fr_450px] gap-8 items-start">
                                {/* Left: Input Form */}
                                <div className="glass-panel p-8 md:p-10 border border-white/10 shadow-2xl bg-black/40 backdrop-blur-xl rounded-3xl">
                                    <div className="flex items-center gap-6 mb-10 pb-8 border-b border-white/10">
                                        <div className="p-4 bg-gradient-to-br from-[rgba(0,255,118,0.15)] to-transparent rounded-2xl border border-white/5 shadow-inner">
                                            {activeTool === 'crop' && <Sprout className="w-10 h-10 text-[hsl(var(--primary))]" />}
                                            {activeTool === 'fertilizer' && <Beaker className="w-10 h-10 text-[hsl(var(--primary))]" />}
                                            {activeTool === 'irrigation' && <Droplets className="w-10 h-10 text-[hsl(var(--primary))]" />}
                                        </div>
                                        <div>
                                            <h3 className="text-3xl font-bold text-white mb-2">
                                                {activeTool === 'crop' ? 'Crop Recommendation' : activeTool === 'fertilizer' ? 'Fertilizer Optimizer' : 'Irrigation Scheduler'}
                                            </h3>
                                            <p className="text-[hsl(var(--text-muted))]">
                                                Configure parameters for the AI model.
                                            </p>
                                        </div>
                                    </div>

                                    <form onSubmit={handlePredict} className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                                        <div className="md:col-span-2">
                                            <div className="flex justify-between items-center mb-6">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-1 h-6 bg-[hsl(var(--highlight))] rounded-full" />
                                                    <h4 className="text-sm font-bold text-white uppercase tracking-wider">Soil Chemistry</h4>
                                                </div>
                                                <button
                                                    type="button"
                                                    onClick={handleFetchSoilData}
                                                    className="text-xs flex items-center gap-2 text-emerald-400 hover:text-white transition-colors px-3 py-1 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 cursor-pointer"
                                                >
                                                    <Database className="w-3 h-3" /> Fetch Live Soil
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                                                <InputField label="Nitrogen (N)" name="n" value={formData.n} onChange={handleInputChange} placeholder="0-140" />
                                                <InputField label="Phosphorus (P)" name="p" value={formData.p} onChange={handleInputChange} placeholder="0-145" />
                                                <InputField label="Potassium (K)" name="k" value={formData.k} onChange={handleInputChange} placeholder="0-205" />
                                            </div>
                                        </div>

                                        <div className="md:col-span-2 border-t border-white/10 pt-8 mt-2">
                                            <div className="flex justify-between items-center mb-6">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-1 h-6 bg-blue-400 rounded-full" />
                                                    <h4 className="text-sm font-bold text-white uppercase tracking-wider">Environment</h4>
                                                </div>
                                                <button
                                                    type="button"
                                                    onClick={handleFetchWeather}
                                                    className="text-xs flex items-center gap-2 text-[hsl(var(--primary))] hover:text-white transition-colors px-3 py-1 rounded-full bg-[hsl(var(--primary))]/10 hover:bg-[hsl(var(--primary))]/20 border border-[hsl(var(--primary))]/20 cursor-pointer"
                                                >
                                                    <Wind className="w-3 h-3" /> Fetch Live Weather
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                                                <InputField label="Temperature (°C)" name="temperature" value={formData.temperature} onChange={handleInputChange} placeholder="e.g. 26" icon={Thermometer} />
                                                <InputField label="Humidity (%)" name="humidity" value={formData.humidity} onChange={handleInputChange} placeholder="e.g. 80" icon={Droplets} />
                                                <InputField label="pH Level" name="ph" value={formData.ph} onChange={handleInputChange} placeholder="0-14" icon={Beaker} />
                                                <InputField label="Rainfall (mm)" name="rainfall" value={formData.rainfall} onChange={handleInputChange} placeholder="e.g. 200" icon={Wind} />
                                            </div>
                                        </div>

                                        <div className="md:col-span-2 mt-8">
                                            <button
                                                type="submit"
                                                disabled={loading}
                                                className="group relative w-full overflow-hidden rounded-xl bg-[hsl(var(--primary))] py-5 text-lg font-bold text-black shadow-[0_0_20px_rgba(0,230,118,0.3)] transition-all hover:scale-[1.01] hover:shadow-[0_0_40px_rgba(0,230,118,0.5)] disabled:opacity-70 disabled:hover:scale-100"
                                            >
                                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                                                <span className="relative flex items-center justify-center gap-3">
                                                    {loading ? (
                                                        <><Activity className="animate-spin w-5 h-5" /> Processing Neural Network...</>
                                                    ) : (
                                                        <><Sparkles className="w-5 h-5" /> Run AI Analysis</>
                                                    )}
                                                </span>
                                            </button>
                                        </div>
                                    </form>
                                </div>

                                {/* Right: Results Panel */}
                                <div className="lg:sticky lg:top-24 space-y-6">
                                    <AnimatePresence mode="wait">
                                        {!result ? (
                                            <motion.div
                                                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                                className="glass-panel p-10 min-h-[400px] flex flex-col items-center justify-center text-center border-dashed border-2 border-white/10 bg-black/20 rounded-3xl"
                                            >
                                                <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center mb-6 animate-pulse">
                                                    <Activity className="w-10 h-10 text-white/20" />
                                                </div>
                                                <h4 className="text-xl font-bold text-white mb-2">Awaiting Input</h4>
                                                <p className="text-[hsl(var(--text-muted))] max-w-[250px] leading-relaxed">
                                                    Fill out the parameters and launch the analysis to see real-time predictions.
                                                </p>
                                            </motion.div>
                                        ) : (
                                            <motion.div
                                                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                className="relative overflow-hidden rounded-3xl border border-[hsl(var(--primary))] bg-gradient-to-b from-black/80 to-[rgba(0,60,20,0.5)] p-0 shadow-[0_0_50px_rgba(0,230,118,0.15)]"
                                            >
                                                {/* Glowing Orb Background */}
                                                <div className="absolute -top-24 -right-24 w-64 h-64 bg-[hsl(var(--primary))] rounded-full blur-[80px] opacity-20 animate-pulse" />

                                                <div className="relative p-8 md:p-10 z-10">
                                                    <div className="flex items-center gap-3 mb-8">
                                                        <div className="w-2 h-2 rounded-full bg-[hsl(var(--primary))] animate-ping" />
                                                        <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-[hsl(var(--primary))]">Analysis Successful</h4>
                                                    </div>

                                                    {/* Dynamic Explanation (XAI) */}
                                                    {/* Dynamic Explanation (XAI Chart) */}
                                                    {result.explain && result.explain.chart_data && (
                                                        <div className="mb-6 p-4 bg-white/5 rounded-xl border border-white/5">
                                                            <div className="text-xs font-bold text-[hsl(var(--text-muted))] uppercase tracking-wider mb-2 flex justify-between">
                                                                <span>AI Decision Factors</span>
                                                                <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded">SHAP Analysis</span>
                                                            </div>
                                                            <div className="h-[200px] w-full">
                                                                <ResponsiveContainer width="100%" height="100%">
                                                                    <BarChart
                                                                        data={result.explain.chart_data}
                                                                        layout="vertical"
                                                                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                                                                    >
                                                                        <XAxis type="number" hide domain={[-10, 10]} />
                                                                        <YAxis dataKey="name" type="category" width={80} tick={{ fill: 'hsl(var(--text-muted))', fontSize: 10 }} />
                                                                        <Tooltip
                                                                            cursor={{ fill: 'transparent' }}
                                                                            content={({ active, payload }) => {
                                                                                if (active && payload && payload.length) {
                                                                                    return (
                                                                                        <div className="bg-black/90 border border-white/10 p-2 rounded text-xs text-white">
                                                                                            <p className="font-bold">{payload[0].payload.name}</p>
                                                                                            <p>Impact: {payload[0].value > 0 ? '+' : ''}{payload[0].value}</p>
                                                                                        </div>
                                                                                    );
                                                                                }
                                                                                return null;
                                                                            }}
                                                                        />
                                                                        <ReferenceLine x={0} stroke="#666" />
                                                                        <Bar dataKey="impact" barSize={10} radius={[4, 4, 4, 4]}>
                                                                            {result.explain.chart_data.map((entry, index) => (
                                                                                <Cell key={`cell-${index}`} fill={entry.impact > 0 ? 'hsl(var(--primary))' : '#ef4444'} />
                                                                            ))}
                                                                        </Bar>
                                                                    </BarChart>
                                                                </ResponsiveContainer>
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* New: Explicit Irrigation Advice for Crop/Fertilizer Tools too */}
                                                    {activeTool !== 'irrigation' && (
                                                        <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-start gap-4">
                                                            <div className="p-2 bg-blue-500/20 rounded-full">
                                                                <Droplets className="w-5 h-5 text-blue-400" />
                                                            </div>
                                                            <div>
                                                                <h5 className="text-sm font-bold text-white mb-1">Watering Advice</h5>
                                                                <p className="text-sm text-blue-200/80 leading-relaxed">
                                                                    {getIrrigationTip(0, formData.temperature)} {/* Using logic helper */}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}

                                                    {activeTool === 'crop' && (
                                                        <div>
                                                            <div className="text-sm font-medium text-[hsl(var(--text-muted))] mb-2">Optimal Crop Identified</div>
                                                            <div className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                                                                {result.prediction}
                                                            </div>

                                                            {/*
                                                            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-gradient-to-r from-[rgba(0,230,118,0.2)] to-transparent border border-[hsl(var(--primary))]">
                                                                <Activity className="w-4 h-4 text-emerald-400" />
                                                                <span className="text-sm font-bold text-emerald-400">
                                                                    {(result.confidence * 100).toFixed(1)}% Confidence
                                                                </span>
                                                            </div>
                                                            */}
                                                        </div>
                                                    )}

                                                    {activeTool === 'fertilizer' && (
                                                        <div>
                                                            <div className="text-sm font-medium text-[hsl(var(--text-muted))] mb-3">Recommended Formula</div>
                                                            <div className="text-xl md:text-2xl font-bold text-white leading-relaxed p-4 rounded-xl bg-white/5 border border-white/10 mb-6">
                                                                {result.recommendation}
                                                            </div>

                                                            {FERTILIZER_INFO[result.recommendation] && (
                                                                <div className="bg-[hsl(var(--primary))]/10 border border-[hsl(var(--primary))]/20 rounded-xl p-4">
                                                                    <div className="flex items-center gap-2 mb-2 text-[hsl(var(--primary))]">
                                                                        <Activity className="w-4 h-4" />
                                                                        <span className="text-sm font-bold uppercase tracking-wider">{FERTILIZER_INFO[result.recommendation].type}</span>
                                                                    </div>
                                                                    <p className="text-sm text-white/80 leading-relaxed">
                                                                        {FERTILIZER_INFO[result.recommendation].tip}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {activeTool === 'irrigation' && (
                                                        <div>
                                                            <div className="text-sm font-medium text-[hsl(var(--text-muted))] mb-3">Irrigation Schedule</div>
                                                            <div className="flex items-baseline gap-2 mb-2">
                                                                <div className="text-6xl font-bold text-white">{result.irrigation_hours}</div>
                                                                <div className="text-xl text-[hsl(var(--text-muted))]">Hours</div>
                                                            </div>
                                                            <p className="text-sm text-[hsl(var(--text-muted))] mb-4">Required today based on current moisture.</p>

                                                            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                                                                <div className="flex items-center gap-3">
                                                                    <Wind className="w-5 h-5 text-blue-400" />
                                                                    <div className="text-sm text-white">Rainfall Forecast: <span className="font-bold">{formData.rainfall} mm</span></div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}

                                                    <div className="mt-10 pt-8 border-t border-white/10">
                                                        <h5 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                                                            <Sparkles className="w-4 h-4 text-yellow-400" /> AI Suggested Action
                                                        </h5>
                                                        <p className="text-sm text-[hsl(var(--text-muted))] leading-relaxed">
                                                            {activeTool === 'irrigation'
                                                                ? getIrrigationTip(result.irrigation_hours, formData.temperature)
                                                                : activeTool === 'fertilizer'
                                                                    ? "Follow the dosage instructions carefully. Consider soil testing again after harvest."
                                                                    : `Based on these results, the system recommends planting ${result.prediction || 'this crop'} for optimal yield.`
                                                            }
                                                        </p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </section>
    );
};

export default RecommendationSection;
