import React, { useEffect, useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Legend
} from 'recharts';
import { Activity, Droplets, Zap, AlertTriangle, Sprout, Thermometer, CloudRain, Sun } from 'lucide-react';
import { subscribeToLiveSoilData, getCurrentWeather } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Removed static mock data for the graph as we will use live rolling data

const StatCard = ({ title, value, unit, icon: Icon, trend, color, subtext }) => {
    // Dynamic color mapping for Tailwind
    const colorStyles = {
        primary: 'text-[#7C6F64] bg-[#7C6F64]/10',
        secondary: 'text-[#8AA89E] bg-[#E6F1EC]', // Rain
        accent: 'text-[#8AA89E] bg-[#E9EFEA]',    // Moisture
        warning: 'text-[#9C8F80] bg-[#F5E9C9]',   // Temperature
        info: 'text-[#6C8FA8] bg-[#E5EFF5]',      // Humidity
    };
    return (
        <div className="card flex flex-col gap-2">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-muted text-sm">{title}</p>
                    <h3 className="h2 mt-1">{value} <span className="text-base font-normal text-text-secondary">{unit}</span></h3>
                    {subtext && <p className="text-xs text-muted mt-1">{subtext}</p>}
                </div>
                <div className={`p-2 rounded-md ${colorStyles[color] || 'text-primary bg-primary/10'}`}>
                    <Icon size={24} />
                </div>
            </div>
            {trend && (
                <div className="flex items-center gap-1 text-sm">
                    <span className={`font-semibold ${trend > 0 ? 'text-primary' : 'text-accent'}`}>
                        {trend > 0 ? '+' : ''}{trend}%
                    </span>
                    <span className="text-muted">vs last week</span>
                </div>
            )}
        </div>
    );
};

import LocationSelector from '../components/LocationSelector';

const Dashboard = () => {
    const { currentUser } = useAuth();
    const [liveData, setLiveData] = useState(null);
    const [weather, setWeather] = useState(null);
    const [weatherError, setWeatherError] = useState(false);
    const [npkHistory, setNpkHistory] = useState([]);

    // Call this to force refresh weather when location changes
    const fetchWeather = async () => {
        setWeatherError(false);
        try {
            const weatherData = await getCurrentWeather();
            setWeather(weatherData);
        } catch (error) {
            console.error("Failed to load weather data", error);
            setWeatherError(true);
        }
    };

    useEffect(() => {
        // Subscribe to live sensors (RTDB)
        const unsubscribe = subscribeToLiveSoilData((data) => {
            setLiveData(data);
            
            setNpkHistory(prev => {
                const now = new Date();
                const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
                
                const newDataPoint = {
                    time: timeString,
                    n: data.n || 0,
                    p: data.p || 0,
                    k: data.k || 0,
                };
                
                // Keep last 15 data points for a smooth rolling window
                const newHistory = [...prev, newDataPoint];
                if (newHistory.length > 15) {
                    return newHistory.slice(newHistory.length - 15);
                }
                return newHistory;
            });
        });

        fetchWeather(); // Initial fetch

        return () => unsubscribe();
    }, []);

    // Helpers to safely get sensor data
    const moisture = liveData?.moisture ?? '--';
    const ph = liveData?.ph ?? '--';
    const nitrogen = liveData?.n ?? '--';
    const phosphorus = liveData?.p ?? '--';
    const potassium = liveData?.k ?? '--';

    // Helpers for weather data
    const temp = weather?.temperature ? Math.round(weather.temperature) : '--';
    const humidity = weather?.humidity ?? '--';
    const rainForecast = weather?.rainfall_forecast_24h ? weather.rainfall_forecast_24h.toFixed(1) : '0.0';
    const weatherDesc = weather?.description ? weather.description.charAt(0).toUpperCase() + weather.description.slice(1) : 'Unknown';

    return (
        <div className="container pb-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="h2">Welcome back, {currentUser?.full_name || 'Farmer'}</h1>
                    <p className="text-muted text-sm mb-2">{currentUser?.role === 'admin' ? 'Administrator' : 'Farmer'} View • Real-time Monitoring</p>
                    <div className="mt-2 text-muted">
                        {/* Location Selector replaces the static text */}
                        <LocationSelector onLocationChanged={fetchWeather} />
                        {weatherError && (
                            <button
                                onClick={fetchWeather}
                                className="text-xs text-accent mt-1 flex items-center gap-1 hover:underline"
                            >
                                <Zap size={12} /> Retry Weather
                            </button>
                        )}
                    </div>
                </div>
                <div>
                    <button className="btn btn-primary">
                        Download Report
                    </button>
                </div>
            </div>

            {/* API WEATHER + LIVE SENSORS */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Weather Data */}
                <StatCard
                    title="Temperature"
                    value={weatherError ? 'Error' : temp}
                    unit={weatherError ? '' : "°C"}
                    icon={Sun}
                    color={weatherError ? "accent" : "warning"}
                    subtext={weatherError ? "Check API Key" : weatherDesc}
                />
                <StatCard
                    title="Humidity"
                    value={weatherError ? 'Error' : humidity}
                    unit={weatherError ? '' : "%"}
                    icon={Droplets}
                    color={weatherError ? "accent" : "info"}
                />
                <StatCard
                    title="Rain Forecast (24h)"
                    value={weatherError ? 'Error' : rainForecast}
                    unit={weatherError ? '' : "mm"}
                    icon={CloudRain}
                    color={weatherError ? "accent" : "secondary"}
                />

                {/* Sensor Data */}
                <StatCard title="Live Moisture" value={moisture} unit="%" icon={Activity} color="accent" />
            </div>

            {/* LIVE SOIL NUTRIENTS */}
            <h3 className="h3 mb-4 text-[#2F2A26]">Live Soil Nutrients</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard title="Nitrogen (N)" value={nitrogen} unit="mg/kg" icon={Sprout} color="primary" />
                <StatCard title="Phosphorus (P)" value={phosphorus} unit="mg/kg" icon={Sprout} color="warning" />
                <StatCard title="Potassium (K)" value={potassium} unit="mg/kg" icon={Sprout} color="info" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 gap-6 mb-8">
                <div className="card">
                    <h3 className="h3 mb-6">Live NPK Variation</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={npkHistory}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E6E0D6" />
                                <XAxis dataKey="time" stroke="#6B6259" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#6B6259" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#FFFFFF',
                                        borderRadius: '12px',
                                        border: '1px solid #E6E0D6',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                                    }}
                                />
                                <Legend iconType="circle" />
                                <Line type="monotone" dataKey="n" stroke="#7C6F64" strokeWidth={3} dot={{ r: 4, fill: '#7C6F64', strokeWidth: 2, stroke: '#FFF' }} activeDot={{ r: 6 }} name="Nitrogen (N)" label={{ position: 'top', fill: '#7C6F64', fontSize: 10, fontWeight: 500 }} />
                                <Line type="monotone" dataKey="p" stroke="#D97706" strokeWidth={3} dot={{ r: 4, fill: '#D97706', strokeWidth: 2, stroke: '#FFF' }} activeDot={{ r: 6 }} name="Phosphorus (P)" label={{ position: 'top', fill: '#D97706', fontSize: 10, fontWeight: 500 }} />
                                <Line type="monotone" dataKey="k" stroke="#3B82F6" strokeWidth={3} dot={{ r: 4, fill: '#3B82F6', strokeWidth: 2, stroke: '#FFF' }} activeDot={{ r: 6 }} name="Potassium (K)" label={{ position: 'top', fill: '#3B82F6', fontSize: 10, fontWeight: 500 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Recent Activity Table */}
            <div className="card overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="h3">Recent Activity</h3>
                    <button className="btn btn-outline text-small">View All</button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-border-color">
                                <th className="p-4 text-text-secondary font-medium">Time</th>
                                <th className="p-4 text-text-secondary font-medium">Event</th>
                                <th className="p-4 text-text-secondary font-medium">Zone</th>
                                <th className="p-4 text-text-secondary font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[
                                { time: '12:30 PM', event: 'Irrigation Cycle Started', zone: 'Zone 2', status: 'Running' },
                                { time: '11:45 AM', event: 'Moisture Alert Low', zone: 'Zone 1', status: 'Resolved' },
                                { time: '09:00 AM', event: 'System Daily Check', zone: 'All', status: 'Completed' },
                            ].map((row, i) => (
                                <tr key={i} className="border-b border-border-color last:border-0 hover:bg-bg-body/50 transition-colors">
                                    <td className="p-4">{row.time}</td>
                                    <td className="p-4 font-medium">{row.event}</td>
                                    <td className="p-4">{row.zone}</td>
                                    <td className="p-4">
                                        <span className={`px-3 py-1 rounded-full text-sm ${row.status === 'Running' ? 'bg-secondary/10 text-secondary' : 'bg-primary/10 text-primary'}`}>
                                            {row.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
