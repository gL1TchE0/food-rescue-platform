import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add auth token
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const apiService = {
    login: (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        return apiClient.post('/auth/login', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
    },
    getMe: () => apiClient.get('/auth/me'),
    getPendingVolunteers: () => apiClient.get('/admin/volunteers?verification_status=PENDING'),
    getVerifiedVolunteers: () => apiClient.get('/admin/volunteers?verification_status=VERIFIED'),
    getRejectedVolunteers: () => apiClient.get('/admin/volunteers?verification_status=REJECTED'),
    approveVolunteer: (id) => apiClient.post(`/admin/volunteers/${id}/approve`),
    rejectVolunteer: (id, reason) => apiClient.post(`/admin/volunteers/${id}/reject`, { reason }),
    getStats: () => apiClient.get('/admin/stats/overview'),
};
