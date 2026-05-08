import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getCurrentWeather, getLatestSoilData, getActiveLocation } from '../services/api';
import { Sprout, Beaker, ChevronRight, Activity, Sparkles, Wind, Droplets, Thermometer, Database, Info, MapPin, Calendar } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ToolCard = ({ title, desc, icon: Icon, onClick }) => (
    <motion.div
        whileHover={{ y: -5, scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
        className="bg-white p-8 cursor-pointer group relative overflow-hidden border border-[#E6E0D6] hover:border-[#7C6F64] transition-all duration-300 shadow-sm hover:shadow-md rounded-[16px]"
    >
        <div className="absolute top-0 right-0 w-32 h-32 bg-[#7C6F64] opacity-[0.03] rounded-full blur-[50px] -mr-16 -mt-16 group-hover:opacity-5 transition-opacity" />

        <div className="w-16 h-16 rounded-2xl bg-[#7C6F64]/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 border border-[#E6E0D6]">
            <Icon className="w-8 h-8 text-[#7C6F64]/70 group-hover:text-[#7C6F64] transition-colors" />
        </div>

        <h3 className="text-2xl font-bold mb-3 text-[#2F2A26] transition-colors">{title}</h3>
        <p className="text-[#6B6259] mb-8 leading-relaxed">{desc}</p>

        <div className="flex items-center text-[#7C6F64] font-bold text-sm uppercase tracking-wide">
            Launch Tool <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
        </div>
    </motion.div>
);

const InputField = ({ label, name, value, onChange, placeholder, icon: Icon }) => (
    <div className="group">
        <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#6B6259] mb-2 ml-1 group-focus-within:text-[#7C6F64] transition-colors">
            {Icon && <Icon className="w-3 h-3" />} {label}
        </label>
        <div className="relative">
            <input
                type={name === 'location' ? 'text' : 'number'}
                name={name}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="w-full bg-[#FBF8F3] border border-[#E3DDD3] rounded-md px-4 py-4 text-[#2F2A26] placeholder-[#9C8F80] focus:border-[#7C6F64] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#7C6F64]/20 transition-all font-medium"
            />
        </div>
    </div>
);

const SelectField = ({ label, name, value, onChange, options, icon: Icon }) => (
    <div className="group">
        <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#6B6259] mb-2 ml-1 group-focus-within:text-[#7C6F64] transition-colors">
            {Icon && <Icon className="w-3 h-3" />} {label}
        </label>
        <div className="relative">
            <select
                name={name}
                value={value}
                onChange={onChange}
                className="w-full bg-[#FBF8F3] border border-[#E3DDD3] rounded-md px-4 py-4 text-[#2F2A26] focus:border-[#7C6F64] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#7C6F64]/20 transition-all font-medium appearance-none"
            >
                {options.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#9C8F80]">
                <ChevronRight className="w-4 h-4 rotate-90" />
            </div>
        </div>
    </div>
);

const RecommendationSection = () => {
    const [activeTool, setActiveTool] = useState(null);
    const [formData, setFormData] = useState({
        n: '', p: '', k: '',
        location: '', month: 'January', ph: '', soilMoisture: '',
        temperature: '', humidity: '', rainfall: '',
        soilType: 'Loamy', cropType: 'Maize'
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        getActiveLocation().then(data => {
            if (data && data.name && data.name !== "Unknown") {
                setFormData(prev => ({ ...prev, location: data.name }));
            }
        });
    }, []);

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
            const payload = {
                location: formData.location || "London",
                month: formData.month,
                n: !isNaN(parseFloat(formData.n)) ? parseFloat(formData.n) : 0.0,
                p: !isNaN(parseFloat(formData.p)) ? parseFloat(formData.p) : 0.0,
                k: !isNaN(parseFloat(formData.k)) ? parseFloat(formData.k) : 0.0,
                temperature: formData.temperature !== '' ? parseFloat(formData.temperature) : null,
                humidity: formData.humidity !== '' ? parseFloat(formData.humidity) : null,
                rainfall: formData.rainfall !== '' ? parseFloat(formData.rainfall) : null,
                ph: !isNaN(parseFloat(formData.ph)) ? parseFloat(formData.ph) : 7.0, // Default pH 7
                soil_moisture: !isNaN(parseFloat(formData.soilMoisture)) ? parseFloat(formData.soilMoisture) : 50.0,
                soilType: formData.soilType === 'Clay' ? 'Clayey' : formData.soilType,
                cropType: formData.cropType
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
            const rainValue = data.rainfall > 0 ? data.rainfall : (data.rainfall_forecast_24h !== undefined ? data.rainfall_forecast_24h : 0);

            setFormData(prev => ({
                ...prev,
                temperature: data.temperature !== undefined ? data.temperature : prev.temperature,
                humidity: data.humidity !== undefined ? data.humidity : prev.humidity,
                rainfall: rainValue !== undefined ? rainValue : prev.rainfall,
                // Removed the heuristic soilMoisture overwrite so it doesn't destroy real sensor data
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
                    n: data.n !== undefined ? data.n : prev.n,
                    p: data.p !== undefined ? data.p : prev.p,
                    k: data.k !== undefined ? data.k : prev.k,
                    ph: data.ph !== undefined ? data.ph : prev.ph,
                    // Removed humidity and temp overwrites to avoid conflicts with Fetch Live Weather
                    soilMoisture: data.moisture !== undefined ? data.moisture : prev.soilMoisture
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
        setFormData({
            n: '', p: '', k: '',
            location: '', month: 'January', ph: '', soilMoisture: '',
            temperature: '', humidity: '', rainfall: '',
            soilType: 'Loamy', cropType: 'Maize'
        });
        setResult(null);
        setError(null);
    };

    return (
        <section id="tools" className="relative py-20 min-h-screen overflow-hidden bg-[#F5F1E8]">
            {/* Ambient Ambient Background Elements */}
            <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[#7C6F64] opacity-[0.02] rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-[#8AA89E] opacity-[0.02] rounded-full blur-[120px] pointer-events-none" />

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
                                    <h2 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight text-[#2F2A26]">
                                        AI <span className="text-[#7C6F64]">Analysis</span>
                                    </h2>
                                    <p className="text-xl text-[#6B6259] max-w-2xl mx-auto leading-relaxed">
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
                                className="group mb-8 flex items-center gap-3 px-5 py-2.5 rounded-full bg-white border border-[#E6E0D6] hover:border-[#7C6F64] transition-all text-sm font-medium text-[#6B6259] hover:text-[#2F2A26] shadow-sm"
                            >
                                <ChevronRight className="w-4 h-4 rotate-180 group-hover:-translate-x-1 transition-transform" />
                                Return to Hub
                            </button>

                            <div className="grid grid-cols-1 lg:grid-cols-[1fr_450px] gap-8 items-start">
                                {/* Left: Input Form */}
                                <div className="bg-white p-8 md:p-10 border border-[#E6E0D6] shadow-sm rounded-3xl">
                                    <div className="flex items-center gap-6 mb-10 pb-8 border-b border-[#E6E0D6]">
                                        <div className="p-4 bg-[#FBF8F3] rounded-2xl border border-[#E6E0D6]">
                                            {activeTool === 'crop' && <Sprout className="w-10 h-10 text-[#7C6F64]" />}
                                            {activeTool === 'fertilizer' && <Beaker className="w-10 h-10 text-[#7C6F64]" />}
                                            {activeTool === 'irrigation' && <Droplets className="w-10 h-10 text-[#7C6F64]" />}
                                        </div>
                                        <div>
                                            <h3 className="text-3xl font-bold text-[#2F2A26] mb-2">
                                                {activeTool === 'crop' ? 'Crop Recommendation' : activeTool === 'fertilizer' ? 'Fertilizer Optimizer' : 'Irrigation Scheduler'}
                                            </h3>
                                            <p className="text-[#6B6259]">
                                                Configure parameters for the AI model.
                                            </p>
                                        </div>
                                    </div>

                                    <form onSubmit={handlePredict} className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                                        <div className="md:col-span-2">
                                            {activeTool !== 'irrigation' && (
                                                <div className="flex justify-between items-center mb-6">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-1 h-6 bg-[#7C6F64] rounded-full" />
                                                        <h4 className="text-sm font-bold text-[#2F2A26] uppercase tracking-wider">Soil Chemistry</h4>
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={handleFetchSoilData}
                                                        className="text-xs flex items-center gap-2 text-[#7C6F64] hover:bg-[#7C6F64]/5 transition-colors px-3 py-1 rounded-full border border-[#7C6F64]/20 cursor-pointer"
                                                    >
                                                        <Database className="w-3 h-3" /> Fetch Live Soil
                                                    </button>
                                                </div>
                                            )}
                                            {activeTool !== 'irrigation' && (
                                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                                                    <InputField label="Nitrogen (N)" name="n" value={formData.n} onChange={handleInputChange} placeholder="0-140" />
                                                    <InputField label="Phosphorus (P)" name="p" value={formData.p} onChange={handleInputChange} placeholder="0-145" />
                                                    <InputField label="Potassium (K)" name="k" value={formData.k} onChange={handleInputChange} placeholder="0-205" />
                                                </div>
                                            )}
                                            {(activeTool === 'fertilizer' || activeTool === 'irrigation') && (
                                                <div className={`grid grid-cols-1 sm:grid-cols-2 gap-5 ${activeTool !== 'irrigation' ? 'mt-5 pt-5 border-t border-[#E6E0D6]' : ''}`}>
                                                    <SelectField
                                                        label="Soil Type"
                                                        name="soilType"
                                                        value={formData.soilType}
                                                        onChange={handleInputChange}
                                                        options={['Sandy', 'Loamy', 'Clay']}
                                                        icon={Database}
                                                    />
                                                    <SelectField
                                                        label="Target Crop"
                                                        name="cropType"
                                                        value={formData.cropType}
                                                        onChange={handleInputChange}
                                                        options={['Barley', 'Cotton', 'Ground Nuts', 'Maize', 'Millets', 'Oil seeds', 'Paddy', 'Pulses', 'Sugarcane', 'Tobacco', 'Wheat']}
                                                        icon={Sprout}
                                                    />
                                                </div>
                                            )}
                                        </div>

                                        <div className="md:col-span-2 border-t border-[#E6E0D6] pt-8 mt-2">
                                            <div className="flex justify-between items-center mb-6">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-1 h-6 bg-[#8AA89E] rounded-full" />
                                                    <h4 className="text-sm font-bold text-[#2F2A26] uppercase tracking-wider">Environment</h4>
                                                </div>
                                                <div className="flex gap-2">
                                                    {activeTool === 'irrigation' && (
                                                        <button
                                                            type="button"
                                                            onClick={handleFetchSoilData}
                                                            className="text-xs flex items-center gap-2 text-[#7C6F64] hover:bg-[#7C6F64]/5 transition-colors px-3 py-1 rounded-full border border-[#7C6F64]/20 cursor-pointer"
                                                        >
                                                            <Database className="w-3 h-3" /> Fetch Live Moisture
                                                        </button>
                                                    )}
                                                    <button
                                                        type="button"
                                                        onClick={handleFetchWeather}
                                                        className="text-xs flex items-center gap-2 text-[#8AA89E] hover:bg-[#8AA89E]/5 transition-colors px-3 py-1 rounded-full border border-[#8AA89E]/20 cursor-pointer"
                                                    >
                                                        <Wind className="w-3 h-3" /> Fetch Live Weather
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-5">
                                                <InputField label="Temperature (°C)" name="temperature" value={formData.temperature} onChange={handleInputChange} placeholder="e.g. 26" icon={Thermometer} />
                                                <InputField label="Humidity (%)" name="humidity" value={formData.humidity} onChange={handleInputChange} placeholder="e.g. 80" icon={Droplets} />
                                                {activeTool !== 'irrigation' && (
                                                    <InputField label="Rainfall (mm)" name="rainfall" value={formData.rainfall} onChange={handleInputChange} placeholder="e.g. 200" icon={Wind} />
                                                )}
                                                {activeTool !== 'irrigation' && (
                                                    <InputField label="pH Level" name="ph" value={formData.ph} onChange={handleInputChange} placeholder="0-14" icon={Beaker} />
                                                )}
                                                {activeTool === 'irrigation' && (
                                                    <InputField label="Soil Moisture (%)" name="soilMoisture" value={formData.soilMoisture} onChange={handleInputChange} placeholder="e.g. 45" icon={Droplets} />
                                                )}
                                            </div>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-5 border-t border-[#E6E0D6]">
                                                <SelectField
                                                    label="Month"
                                                    name="month"
                                                    value={formData.month}
                                                    onChange={handleInputChange}
                                                    options={['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}
                                                    icon={Calendar}
                                                />
                                            </div>
                                        </div>

                                        <div className="md:col-span-2 mt-8">
                                            <button
                                                type="submit"
                                                disabled={loading}
                                                className="group relative w-full overflow-hidden rounded-xl bg-[#7C6F64] py-5 text-lg font-bold text-white shadow-lg transition-all hover:brightness-110 active:scale-[0.98] disabled:opacity-70 disabled:hover:scale-100"
                                            >
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
                                                className="bg-[#FBF8F3] p-10 min-h-[400px] flex flex-col items-center justify-center text-center border-dashed border-2 border-[#E6E0D6] rounded-3xl"
                                            >
                                                <div className="w-24 h-24 rounded-full bg-[#EDE7DC] flex items-center justify-center mb-6 animate-pulse">
                                                    <Activity className="w-10 h-10 text-[#7C6F64]/20" />
                                                </div>
                                                <h4 className="text-xl font-bold text-[#2F2A26] mb-2">Awaiting Input</h4>
                                                <p className="text-[#6B6259] max-w-[250px] leading-relaxed">
                                                    Fill out the parameters and launch the analysis to see real-time predictions.
                                                </p>
                                            </motion.div>
                                        ) : (
                                            <motion.div
                                                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                className="relative overflow-hidden rounded-3xl border border-[#7C6F64] bg-white p-0 shadow-xl"
                                            >
                                                {/* Glowing Orb Background */}
                                                <div className="absolute -top-24 -right-24 w-64 h-64 bg-[#7C6F64] rounded-full blur-[80px] opacity-[0.03] animate-pulse" />

                                                <div className="relative p-8 md:p-10 z-10">
                                                    <div className="flex items-center gap-3 mb-8">
                                                        <div className="w-2 h-2 rounded-full bg-[#8AA89E] animate-ping" />
                                                        <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-[#8AA89E]">Analysis Successful</h4>
                                                    </div>

                                                    {/* XAI Link */}
                                                    {result.explain && (
                                                        <div className="mb-6 p-4 bg-[#FBF8F3] rounded-xl border border-[#E6E0D6]">
                                                            <div className="flex items-center justify-between mb-2">
                                                                <div className="flex items-center gap-2">
                                                                    <Info size={14} className="text-[#7C6F64]" />
                                                                    <span className="text-xs font-bold text-[#2F2A26] uppercase tracking-wider">AI Insights Available</span>
                                                                </div>
                                                                <Link to="/explainable-ai" className="text-[10px] font-bold text-[#7C6F64] hover:underline flex items-center gap-1">
                                                                    View Details <ChevronRight size={10} />
                                                                </Link>
                                                            </div>
                                                            <p className="text-[11px] text-[#6B6259]">
                                                                Detailed feature importance breakdown is in the Explainable AI section.
                                                            </p>
                                                        </div>
                                                    )}


                                                    {activeTool === 'crop' && (
                                                        <div>
                                                            <div className="text-sm font-medium text-[#6B6259] mb-2">Optimal Crop Identified</div>
                                                            <div className="text-5xl md:text-6xl font-bold text-[#2F2A26] mb-6 tracking-tight">
                                                                {result.prediction}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {activeTool === 'fertilizer' && (
                                                        <div>
                                                            <div className="text-sm font-medium text-[#6B6259] mb-3">Recommended Formula</div>
                                                            <div className="text-xl md:text-2xl font-bold text-[#2F2A26] leading-relaxed p-4 rounded-xl bg-[#FBF8F3] border border-[#E6E0D6] mb-6">
                                                                {result.prediction}
                                                            </div>

                                                            {FERTILIZER_INFO[result.prediction] && (
                                                                <div className="bg-[#8AA89E]/10 border border-[#8AA89E]/20 rounded-xl p-4">
                                                                    <div className="flex items-center gap-2 mb-2 text-[#8AA89E]">
                                                                        <Activity className="w-4 h-4" />
                                                                        <span className="text-sm font-bold uppercase tracking-wider">{FERTILIZER_INFO[result.prediction].type}</span>
                                                                    </div>
                                                                    <p className="text-sm text-[#2F2A26] leading-relaxed">
                                                                        {FERTILIZER_INFO[result.prediction].tip}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}

                                                    {activeTool === 'irrigation' && (
                                                        <div className="py-6">
                                                            <div className="p-6 bg-[#8AA89E]/10 border border-[#8AA89E]/20 rounded-2xl flex items-center gap-4">
                                                                <div className="w-12 h-12 bg-[#8AA89E]/20 rounded-full flex items-center justify-center text-[#8AA89E]">
                                                                    <Droplets size={24} />
                                                                </div>
                                                                <div>
                                                                    <h5 className="text-lg font-bold text-[#2F2A26] mb-1">{result.status || "Moisture Analysis"}</h5>
                                                                    <p className="text-sm text-[#6B6259]">
                                                                        {result.irrigation_hours > 0
                                                                            ? `We recommend running the irrigation system for ${result.irrigation_hours} hours.`
                                                                            : "Current soil moisture is sufficient. No irrigation required at this time."}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}

                                                    <div className="mt-6 pt-6 border-t border-[#E6E0D6]">
                                                        <h5 className="text-sm font-bold text-[#2F2A26] mb-2 flex items-center gap-2">
                                                            <Sparkles className="w-4 h-4 text-[#7C6F64]" /> AI Advice
                                                        </h5>
                                                        <p className="text-sm text-[#6B6259] leading-relaxed">
                                                            {activeTool === 'irrigation'
                                                                ? (result.ai_advice || "Soil moisture is sufficient. Irrigation not required.")
                                                                : activeTool === 'fertilizer'
                                                                    ? "Follow the dosage instructions carefully. Your soil has nutrient gaps that this fertilizer will address."
                                                                    : `Based on these results, we recommend planting ${result.prediction || 'this crop'} for optimal yield.`
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
