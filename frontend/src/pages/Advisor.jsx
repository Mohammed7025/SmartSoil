import React from 'react';
import AdvisorSection from '../sections/AdvisorSection';

const Advisor = () => {
    return (
        <div className="pt-24 min-h-screen bg-[hsl(var(--bg-dark))]">
            <div className="absolute top-0 right-0 w-full h-[500px] bg-gradient-to-b from-[hsl(var(--primary))] to-transparent opacity-5 pointer-events-none" />
            <AdvisorSection />
        </div>
    );
};

export default Advisor;
