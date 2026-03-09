import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../api/apiService';

export const useAuth = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchUser = useCallback(async () => {
        try {
            setLoading(true);
            const res = await apiService.getMe();
            setUser(res.data);
            setError(null);
        } catch (err) {
            setUser(null);
            if (err.response?.status !== 401) {
                setError(err.message);
            }
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            fetchUser();
        } else {
            // Auto-login bypass for development
            setUser({
                full_name: 'Default Dispatcher',
                email: 'dispatcher@rescue.org',
                role: 'ADMIN'
            });
            setLoading(false);
        }
    }, [fetchUser]);

    const login = async (email, password) => {
        try {
            setLoading(true);
            const res = await apiService.login(email, password);
            localStorage.setItem('auth_token', res.data.access_token);
            await fetchUser();
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
            return false;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('auth_token');
        setUser(null);
    };

    return { user, loading, error, login, logout, isAuthenticated: !!user };
};
