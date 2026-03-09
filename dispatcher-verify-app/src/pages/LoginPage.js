import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { LogIn, ShieldCheck } from 'lucide-react';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, error } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        await login(email, password);
        setLoading(false);
    };

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100vh',
            padding: '1rem'
        }}>
            <div className="glass-card" style={{
                width: '100%',
                maxWidth: '400px',
                padding: '2.5rem',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* Glow effect */}
                <div style={{
                    position: 'absolute',
                    top: '-20%',
                    left: '-20%',
                    width: '60%',
                    height: '60%',
                    background: 'radial-gradient(circle, rgba(251, 146, 60, 0.15) 0%, transparent 70%)',
                    zIndex: 0
                }} />

                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
                        <div style={{
                            background: 'var(--primary)',
                            padding: '0.5rem',
                            borderRadius: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <ShieldCheck size={24} color="black" />
                        </div>
                        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Dispatcher Verify</h1>
                    </div>

                    <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                        Internal verification portal for food rescue volunteers.
                    </p>

                    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                        {error && (
                            <div style={{
                                background: 'rgba(239, 68, 68, 0.1)',
                                color: 'var(--error)',
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                fontSize: '0.875rem',
                                border: '1px solid rgba(239, 68, 68, 0.2)'
                            }}>
                                {error}
                            </div>
                        )}

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Email Address</label>
                            <input
                                type="email"
                                className="glass-input"
                                placeholder="dispatcher@rescue.org"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            <label style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Password</label>
                            <input
                                type="password"
                                className="glass-input"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                            style={{ marginTop: '0.5rem' }}
                        >
                            {loading ? 'Authenticating...' : (
                                <>
                                    <LogIn size={18} />
                                    Sign In
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
