import axios from 'axios';
import { db, rtdb } from '../config/firebase'; // Ensure rtdb is exported from config
import { collection, getDocs, addDoc } from 'firebase/firestore';
import { ref, onValue, off } from 'firebase/database';

// 1. FASTAPI CONNECTION
// ---------------------
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getIrrigationPrediction = async (sensorData) => {
    try {
        const response = await api.post('/predict/irrigation', sensorData);
        return response.data;
    } catch (error) {
        console.error("AI Prediction Error:", error);
        throw error;
    }
};

export const getCropRecommendation = async (soilData) => {
    try {
        const response = await api.post('/predict/crop', soilData);
        return response.data;
    } catch (error) {
        console.error("Crop ID Error:", error);
        throw error;
    }
};

// 2. WEATHER & LOCATION API
// -------------------------
export const getCurrentWeather = async (lat = null, lon = null) => {
    try {
        const response = await api.post('/weather/current', { lat, lon });
        return response.data;
    } catch (error) {
        console.error("Weather API Error:", error);
        throw error;
    }
};

export const searchLocations = async (query) => {
    try {
        const response = await api.get(`/locations/search?q=${query}`);
        return response.data;
    } catch (error) {
        console.error("Location Search Error:", error);
        return [];
    }
};

export const selectLocation = async (location) => {
    try {
        const response = await api.post('/locations/select', location);
        return response.data;
    } catch (error) {
        console.error("Location Selection Error:", error);
        throw error;
    }
};

export const getActiveLocation = async () => {
    try {
        const response = await api.get('/locations/active');
        return response.data;
    } catch (error) {
        return { name: "Unknown" };
    }
};

// 3. REALTIME DATABASE CONNECTION (Live Sensors)
// ----------------------------------------------
// Matches Flutter: FirebaseDatabase.instance.ref('soilData/latest')
export const subscribeToLiveSoilData = (callback) => {
    const soilRef = ref(rtdb, 'soilData/latest');

    // Listen for data changes
    const unsubscribe = onValue(soilRef, (snapshot) => {
        const data = snapshot.val();
        callback(data || {});
    }, (error) => {
        console.error("RTDB Error:", error);
    });

    // Return unsubscribe function for cleanup
    return () => off(soilRef, 'value', unsubscribe);
};

export const getLatestSoilData = async () => {
    const soilRef = ref(rtdb, 'soilData/latest');
    return new Promise((resolve) => {
        // fast one-time fetch
        onValue(soilRef, (snapshot) => {
            resolve(snapshot.val() || {});
        }, { onlyOnce: true });
    });
};

// 3. FIRESTORE CONNECTION (Logs/Actions)
export const getSensorLogs = async () => {
    try {
        const querySnapshot = await getDocs(collection(db, "sensors"));
        return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error("Firestore Error:", error);
        return [];
    }
};

export const saveManualOverride = async (action) => {
    try {
        // Writing to "actions" collection just like the mobile app might
        await addDoc(collection(db, "actions"), {
            type: action, // e.g., "PUMP_ON"
            timestamp: new Date().toISOString(),
            source: "web_dashboard"
        });
    } catch (error) {
        console.error("Firestore Write Error:", error);
    }
};

export default api;
