import axios from 'axios';
import { db, rtdb } from '../config/firebase'; // Ensure rtdb is exported from config
import { collection, getDocs, addDoc } from 'firebase/firestore';
import { ref, onValue, off, get } from 'firebase/database';

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

export const updateProfile = async (profileData) => {
    try {
        const response = await api.put('/auth/update-profile', profileData);
        return response.data;
    } catch (error) {
        console.error("Profile Update Error:", error);
        throw error;
    }
};

export const changePassword = async (passwordData) => {
    try {
        const response = await api.put('/auth/change-password', passwordData);
        return response.data;
    } catch (error) {
        console.error("Password Change Error:", error);
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
// Function to normalize NPK data from Arduino
const normalizeData = (data) => {
    if (!data) return {};
    return {
        n: data.Nitrogen ?? data.n ?? 0,
        p: data.Phosphorus ?? data.p ?? 0,
        k: data.Potassium ?? data.k ?? 0,
        temperature: data.Temperature ?? data.temperature ?? 0,
        humidity: data.Humidity ?? data.humidity ?? 0,
        moisture: data.SoilMoisture ?? data.Moisture ?? data.moisture ?? 0,
        ph: data.pH ?? data.ph ?? 7.0,
        ...data // Keep original fields just in case
    };
};

export const subscribeToLiveSoilData = (callback) => {
    const soilRef = ref(rtdb, 'NPK');

    // Listen for data changes
    const unsubscribe = onValue(soilRef, (snapshot) => {
        const data = snapshot.val();
        callback(normalizeData(data));
    }, (error) => {
        console.error("RTDB Error:", error);
    });

    // Return unsubscribe function for cleanup
    return () => off(soilRef, 'value', unsubscribe);
};

let soilHistory = [];
const historyRef = ref(rtdb, 'NPK');
onValue(historyRef, (snapshot) => {
    const data = snapshot.val();
    if (data) {
        soilHistory.push(normalizeData(data));
        if (soilHistory.length > 5) {
            soilHistory.shift(); // Keep only last 5 readings
        }
    }
});

export const getLatestSoilData = async () => {
    try {
        const snapshot = await get(ref(rtdb, 'NPK'));
        if (snapshot.exists()) {
            return normalizeData(snapshot.val());
        }
        return null;
    } catch (error) {
        console.error("Error fetching latest soil data:", error);
        return null;
    }
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
