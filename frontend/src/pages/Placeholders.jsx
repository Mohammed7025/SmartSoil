import React, { useEffect, useState } from 'react';
import { subscribeToLiveSoilData } from '../services/api';
import { Droplets, Activity, Thermometer, Sprout } from 'lucide-react';

export const LiveData = () => {
    const [data, setData] = useState(null);
    const [lastUpdated, setLastUpdated] = useState('--:--:--');

    useEffect(() => {
        const unsubscribe = subscribeToLiveSoilData((newData) => {
            setData(newData);
            setLastUpdated(new Date().toLocaleTimeString());
        });
        return () => unsubscribe();
    }, []);

    if (!data) {
        return (
            <div className="container">
                <h1 className="h2" style={{ marginBottom: '1rem' }}>Live Sensor Data</h1>
                <div className="card" style={{ padding: '2rem', textAlign: 'center' }}>
                    <p className="text-muted">Connecting to sensors...</p>
                </div>
            </div>
        );
    }

    const readings = [
        { label: "Moisture Content", value: data.moisture ?? 0, unit: "%", icon: Droplets, color: "#0D7324" },
        { label: "Soil pH", value: data.ph ?? 0, unit: "pH", icon: Activity, color: "#0A84D1" },
        { label: "Nitrogen (N)", value: data.n ?? 0, unit: "mg/kg", icon: Sprout, color: "#8B5CF6" },
        { label: "Phosphorus (P)", value: data.p ?? 0, unit: "mg/kg", icon: Thermometer, color: "#F59E0B" },
        { label: "Potassium (K)", value: data.k ?? 0, unit: "mg/kg", icon: Sprout, color: "#EC4899" },
        { label: "Temperature", value: "24.5", unit: "°C", icon: Thermometer, color: "#EF4444" }, // Mock if not in DB
        { label: "Humidity", value: "60", unit: "%", icon: Droplets, color: "#3B82F6" },         // Mock if not in DB
    ];

    return (
        <div className="container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 className="h2">Live Sensor Readings</h1>
                    <p className="text-muted">Real-time telemetry from Field Unit 1</p>
                </div>
                <div className="card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ height: '8px', width: '8px', borderRadius: '50%', backgroundColor: '#22c55e', display: 'inline-block' }}></span>
                    <span className="text-small" style={{ fontWeight: 600 }}>Live Updates</span>
                </div>
            </div>

            <div className="grid-2">
                {readings.map((item, idx) => (
                    <div key={idx} className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', transition: 'all 0.3s' }}>
                        <div style={{
                            width: '48px', height: '48px',
                            borderRadius: '12px',
                            backgroundColor: `${item.color}20`,
                            color: item.color,
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}>
                            <item.icon size={24} />
                        </div>
                        <div>
                            <p className="text-muted text-small" style={{ marginBottom: '0.25rem' }}>{item.label}</p>
                            <h3 className="h2" style={{ margin: 0 }}>
                                {item.value} <span style={{ fontSize: '1rem', color: 'hsl(var(--text-secondary))', fontWeight: 400 }}>{item.unit}</span>
                            </h3>
                        </div>
                    </div>
                ))}
            </div>

            <div className="card" style={{ marginTop: '2rem' }}>
                <h3 className="h3" style={{ marginBottom: '1rem' }}>Raw Data Stream</h3>
                <pre style={{
                    background: 'hsl(var(--bg-body))',
                    padding: '1rem',
                    borderRadius: 'var(--radius-sm)',
                    overflowX: 'auto',
                    fontSize: '0.85rem'
                }}>
                    {JSON.stringify(data, null, 2)}
                </pre>
                <p className="text-muted text-small" style={{ marginTop: '0.5rem', textAlign: 'right' }}>
                    Last received: {lastUpdated}
                </p>
            </div>
        </div>
    );
};

export const Settings = () => (
    <div className="container">
        <h1 className="h2">Settings</h1>
        <div className="card mt-4">
            <p>User and System settings.</p>
        </div>
    </div>
);
