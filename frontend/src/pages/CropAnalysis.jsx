import React from 'react';
import RecommendationSection from '../sections/RecommendationSection';

const CropAnalysis = () => {
    return (
        <div>
            {/* The RecommendationSection contains its own container and styling. 
                We just wrap it here to fit the routing structure. */}
            <RecommendationSection />
        </div>
    );
};

export default CropAnalysis;
