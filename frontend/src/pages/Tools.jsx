import React from 'react';
import RecommendationSection from '../sections/RecommendationSection';

const Tools = () => {
    return (
        <div className="pt-24 min-h-screen bg-[hsl(var(--bg-dark))]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-gradient-to-b from-[hsl(var(--accent))] to-transparent opacity-5 pointer-events-none" />
            <RecommendationSection />
        </div>
    );
};

export default Tools;
