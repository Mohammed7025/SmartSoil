import React from 'react';

const IrrigationControl = () => {
    return (
        <div className="container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 className="h2">Irrigation Control</h1>
                    <p className="text-muted">Manage water usage and override automated systems.</p>
                </div>
                <div className="card" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Anti-Gravity Mode</span>
                    <label style={{ position: 'relative', display: 'inline-block', width: '48px', height: '24px' }}>
                        <input type="checkbox" style={{ opacity: 0, width: 0, height: 0 }} />
                        <span style={{
                            position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0,
                            backgroundColor: '#ccc', transition: '.4s', borderRadius: '34px'
                        }}></span>
                        <span style={{
                            position: 'absolute', content: '""', height: '18px', width: '18px', left: '3px', bottom: '3px',
                            backgroundColor: 'white', transition: '.4s', borderRadius: '50%'
                        }}></span>
                    </label>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <h3 className="h3" style={{ marginBottom: '1rem' }}>Zone Status</h3>
                    {/* Placeholder for zones */}
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {[1, 2, 3, 4].map(zone => (
                            <div key={zone} style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', background: 'hsl(var(--bg-body))', borderRadius: 'var(--radius-sm)' }}>
                                <span>Zone {zone}</span>
                                <span style={{ color: zone % 2 === 0 ? 'var(--primary)' : 'var(--text-secondary)' }}>
                                    {zone % 2 === 0 ? 'Active' : 'Idle'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="card">
                    <h3 className="h3" style={{ marginBottom: '1rem' }}>Moisture Levels</h3>
                    <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'hsl(var(--bg-body))', borderRadius: 'var(--radius-sm)' }}>
                        <p className="text-muted">Graph Placeholder</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IrrigationControl;
