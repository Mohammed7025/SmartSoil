import React, { useEffect, useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Legend
} from 'recharts';
import { Activity, Droplets, Zap, AlertTriangle, Sprout, Thermometer, CloudRain, Sun } from 'lucide-react';
import { subscribeToLiveSoilData, getCurrentWeather } from '../services/api';

const data = [
    { time: '00:00', moisture: 30, temp: 24 },
    { time: '04:00', moisture: 28, temp: 23 },
    { time: '08:00', moisture: 25, temp: 26 },
    { time: '12:00', moisture: 45, temp: 30 }, // Irrigation happened
    { time: '16:00', moisture: 40, temp: 29 },
    { time: '20:00', moisture: 38, temp: 26 },
    { time: '24:00', moisture: 35, temp: 25 },
];

const waterData = [
    { name: 'Mon', usage: 400 },
    { name: 'Tue', usage: 300 },
    { name: 'Wed', usage: 550 },
    { name: 'Thu', usage: 450 },
    { name: 'Fri', usage: 380 },
    { name: 'Sat', usage: 420 },
    { name: 'Sun', usage: 390 },
];

const StatCard = ({ title, value, unit, icon: Icon, trend, color, subtext }) => {
    // Dynamic color mapping for Tailwind
    const colorStyles = {
        primary: 'text-primary bg-primary/10',
        secondary: 'text-secondary bg-secondary/10',
        accent: 'text-accent bg-accent/10',
        warning: 'text-yellow-500 bg-yellow-500/10',
        info: 'text-blue-500 bg-blue-500/10',
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
    const [liveData, setLiveData] = useState(null);
    const [weather, setWeather] = useState(null);

    // Call this to force refresh weather when location changes
    const fetchWeather = async () => {
        try {
            const weatherData = await getCurrentWeather();
            setWeather(weatherData);
        } catch (error) {
            console.error("Failed to load weather data", error);
        }
    };

    useEffect(() => {
        // Subscribe to live sensors (RTDB)
        const unsubscribe = subscribeToLiveSoilData((data) => {
            setLiveData(data);
        });

        fetchWeather(); // Initial fetch

        return () => unsubscribe();
    }, []);

    // Helpers to safely get sensor data
    const moisture = liveData?.moisture ?? '--';
    const ph = liveData?.ph ?? '--';
    const nitrogen = liveData?.n ?? '--';
    const phosphorus = liveData?.p ?? '--';

    // Helpers for weather data
    const temp = weather?.temperature ? Math.round(weather.temperature) : '--';
    const humidity = weather?.humidity ?? '--';
    const rainForecast = weather?.rainfall_forecast_24h ? weather.rainfall_forecast_24h.toFixed(1) : '0.0';
    const weatherDesc = weather?.description ? weather.description.charAt(0).toUpperCase() + weather.description.slice(1) : 'Unknown';

    return (
        <div className="container pb-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="h2">Farm Overview</h1>
                    <div className="mt-2 text-muted">
                        {/* Location Selector replaces the static text */}
                        <LocationSelector onLocationChanged={fetchWeather} />
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
                    value={temp}
                    unit="°C"
                    icon={Sun}
                    color="warning"
                    subtext={weatherDesc}
                />
                <StatCard
                    title="Humidity"
                    value={humidity}
                    unit="%"
                    icon={Droplets}
                    color="info"
                />
                <StatCard
                    title="Rain Forecast (24h)"
                    value={rainForecast}
                    unit="mm"
                    icon={CloudRain}
                    color="secondary"
                />

                {/* Sensor Data */}
                <StatCard title="Live Moisture" value={moisture} unit="%" icon={Activity} color="accent" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="card">
                    <h3 className="h3 mb-6">Soil Moisture Trends</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                <XAxis dataKey="time" stroke="hsl(var(--text-secondary))" />
                                <YAxis stroke="hsl(var(--text-secondary))" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--bg-surface))', borderRadius: '8px', border: '1px solid hsl(var(--border-color))' }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="moisture" stroke="hsl(var(--secondary))" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} name="Moisture %" />
                                <Line type="monotone" dataKey="temp" stroke="hsl(var(--accent))" strokeWidth={2} dot={false} name="Temp °C" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="card">
                    <h3 className="h3 mb-6">Weekly Water Usage</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={waterData}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.3} vertical={false} />
                                <XAxis dataKey="name" stroke="hsl(var(--text-secondary))" />
                                <YAxis stroke="hsl(var(--text-secondary))" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--bg-surface))', borderRadius: '8px', border: '1px solid hsl(var(--border-color))' }}
                                    cursor={{ fill: 'hsl(var(--bg-body))' }}
                                />
                                <Bar dataKey="usage" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Liters" />
                            </BarChart>
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
