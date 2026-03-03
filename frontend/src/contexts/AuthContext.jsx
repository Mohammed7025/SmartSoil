import React, { createContext, useContext, useEffect, useState } from 'react';

// NOTE: Switched to Mock Auth to match the Flutter Mobile App behavior.
// The user currently uses a MockService in Flutter, so we should mirror that.
// Real Firebase Auth can be enabled later.

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    async function login(email, password) {
        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) throw new Error('Login failed');

            const data = await response.json();
            const user = data.user;

            setCurrentUser(user);
            localStorage.setItem('smartSoilUser', JSON.stringify(user));
            return user;
        } catch (error) {
            console.error("Login error:", error);
            throw error;
        }
    }

    async function signup(email, password, fullName) {
        try {
            const response = await fetch('http://localhost:8000/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, full_name: fullName })
            });

            if (!response.ok) throw new Error('Signup failed');
            return true;
        } catch (error) {
            console.error("Signup error:", error);
            throw error;
        }
    }

    function logout() {
        setCurrentUser(null);
        localStorage.removeItem('smartSoilUser');
        return Promise.resolve();
    }

    // Persist session
    useEffect(() => {
        const storedUser = localStorage.getItem('smartSoilUser');
        if (storedUser) {
            setCurrentUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const value = {
        currentUser,
        login,
        signup,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
