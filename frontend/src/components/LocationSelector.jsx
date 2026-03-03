import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, Loader2 } from 'lucide-react';
import { searchLocations, selectLocation, getActiveLocation } from '../services/api';

const LocationSelector = ({ onLocationChanged }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [activeLocation, setActiveLocation] = useState('Loading...');
    const wrapperRef = useRef(null);

    // Load initial active location
    useEffect(() => {
        getActiveLocation().then(loc => {
            if (loc && loc.name) setActiveLocation(loc.name);
        });
    }, []);

    // Handle outside click to close dropdown
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSearch = async (e) => {
        const val = e.target.value;
        setQuery(val);

        if (val.length > 2) {
            setLoading(true);
            setIsOpen(true);
            const data = await searchLocations(val);
            setResults(data);
            setLoading(false);
        } else {
            setResults([]);
            setIsOpen(false);
        }
    };

    const handleSelect = async (loc) => {
        try {
            await selectLocation(loc);
            setActiveLocation(loc.name);
            setIsOpen(false);
            setQuery('');
            if (onLocationChanged) onLocationChanged();
        } catch (error) {
            console.error("Failed to set location", error);
        }
    };

    return (
        <div className="relative" ref={wrapperRef}>
            <div className="flex items-center gap-3">
                <div className="relative">
                    <input
                        type="text"
                        value={query}
                        onChange={handleSearch}
                        placeholder="Search Farm Location..."
                        className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[hsl(var(--primary))] focus:ring-1 focus:ring-[hsl(var(--primary))] w-64 transition-all shadow-sm"
                    />
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-full shadow-sm">
                    <MapPin className="w-3.5 h-3.5 text-[hsl(var(--primary))]" />
                    <span className="text-xs font-semibold text-gray-700 max-w-[150px] truncate">
                        {activeLocation}
                    </span>
                </div>
            </div>

            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden z-50">
                    {loading ? (
                        <div className="p-4 flex justify-center">
                            <Loader2 className="w-5 h-5 text-[hsl(var(--primary))] animate-spin" />
                        </div>
                    ) : results.length > 0 ? (
                        <ul>
                            {results.map((loc, idx) => (
                                <li
                                    key={idx}
                                    onClick={() => handleSelect(loc)}
                                    className="px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center gap-3 border-b border-gray-100 last:border-0 transition-colors"
                                >
                                    <MapPin className="w-4 h-4 text-gray-400" />
                                    <div className="text-sm text-gray-800">
                                        {loc.name}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className="p-4 text-center text-xs text-gray-500">
                            No locations found
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default LocationSelector;
