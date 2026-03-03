import React from 'react';
import { Thermometer, Droplets, CloudRain, Wind } from 'lucide-react';
import { motion } from 'framer-motion';

const SensorCard = ({ title, value, unit, icon: Icon, color }) => (
    <motion.div
        whileHover={{ y: -5 }}
        className="glass-panel p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group"
    >
        <div className={`absolute top-0 right-0 w-24 h-24 bg-${color}-500 opacity-10 rounded-full blur-2xl -mr-10 -mt-10 group-hover:opacity-20 transition-opacity`} />

        <div className="mb-4 p-3 rounded-full bg-[rgba(255,255,255,0.05)]">
            <Icon className={`w-8 h-8 text-${color}-400`} />
        </div>

        <h3 className="text-[hsl(var(--text-muted))] text-sm font-medium uppercase tracking-wider mb-1">{title}</h3>
        <div className="text-3xl font-bold text-[hsl(var(--text-primary))]">
            {value} <span className="text-lg text-[hsl(var(--text-secondary))]">{unit}</span>
        </div>
    </motion.div>
);

const DashboardSection = () => {
    // Mock Data - Will be replaced by API
    const sensorData = [
        { title: 'Temperature', value: '24', unit: '°C', icon: Thermometer, color: 'orange' },
        { title: 'Humidity', value: '65', unit: '%', icon: Droplets, color: 'blue' },
        { title: 'Soil Moisture', value: '42', unit: '%', icon: CloudRain, color: 'emerald' },
        { title: 'N-P-K Level', value: 'Optimal', unit: '', icon: Wind, color: 'purple' },
    ];

    return (
        <section id="dashboard" className="py-20 relative">
            <div className="container">
                <div className="mb-12 text-center">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">Live Soil <span className="text-gradient">Monitor</span></h2>
                    <p className="text-[hsl(var(--text-muted))]">Real-time sensor readings from your device.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {sensorData.map((sensor, index) => (
                        <SensorCard key={index} {...sensor} />
                    ))}
                </div>

                {/* Graph Placeholder */}
                <div className="mt-8 glass-panel h-64 flex items-center justify-center text-[hsl(var(--text-muted))]">
                    [Live Chart Visualization Component]
                </div>
            </div>
        </section>
    );
};

export default DashboardSection;
