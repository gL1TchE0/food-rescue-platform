import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../api/apiService';
import {
    Users, CheckCircle, XCircle, Clock,
    Menu, LogOut, RefreshCw, ChevronRight,
    ShieldAlert
} from 'lucide-react';
import VolunteerList from '../components/Verification/VolunteerList';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('PENDING');

    const fetchStats = async () => {
        try {
            const res = await apiService.getStats();
            setStats(res.data);
        } catch (err) {
            console.error('Failed to fetch stats', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 30000); // Polling for live impact
        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            {/* Sidebar */}
            <aside className="glass-card" style={{
                width: '280px',
                position: 'fixed',
                height: 'calc(100vh - 2rem)',
                margin: '1rem',
                borderRadius: '1.5rem',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 10
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
                    <div style={{ background: 'var(--primary)', padding: '0.4rem', borderRadius: '0.5rem' }}>
                        <ShieldAlert size={20} color="black" />
                    </div>
                    <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>Verify Central</span>
                </div>

                <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <SidebarLink
                        icon={<Clock size={18} />}
                        text="Pending Review"
                        active={activeTab === 'PENDING'}
                        onClick={() => setActiveTab('PENDING')}
                    />
                    <SidebarLink
                        icon={<CheckCircle size={18} />}
                        text="Verified"
                        active={activeTab === 'VERIFIED'}
                        onClick={() => setActiveTab('VERIFIED')}
                    />
                    <SidebarLink
                        icon={<XCircle size={18} />}
                        text="Rejected"
                        active={activeTab === 'REJECTED'}
                        onClick={() => setActiveTab('REJECTED')}
                    />
                </nav>

                <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--glass-border)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            background: 'var(--secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.8rem',
                            fontWeight: 'bold'
                        }}>
                            {user?.full_name?.charAt(0)}
                        </div>
                        <div style={{ overflow: 'hidden' }}>
                            <div style={{ fontSize: '0.875rem', fontWeight: '600', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                                {user?.full_name}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Dispatcher</div>
                        </div>
                    </div>
                    <button className="btn btn-secondary" style={{ width: '100%' }} onClick={logout}>
                        <LogOut size={18} />
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main style={{ marginLeft: '320px', flex: 1, padding: '2rem 2rem 2rem 0' }}>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
                    <div>
                        <h2 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Volunteer Verification</h2>
                        <p style={{ color: 'var(--text-muted)' }}>Mange and verify new volunteer applications.</p>
                    </div>
                    <button className="btn btn-secondary" onClick={() => { setLoading(true); fetchStats(); }}>
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </header>

                {/* Stats Grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                    gap: '1.5rem',
                    marginBottom: '3rem'
                }}>
                    <StatCard
                        icon={<Clock color="var(--primary)" />}
                        label="Awaiting Review"
                        value={stats?.volunteers?.pending || 0}
                        color="var(--primary)"
                    />
                    <StatCard
                        icon={<Users color="var(--secondary)" />}
                        label="Total Volunters"
                        value={stats?.users?.volunteers || 0}
                        color="var(--secondary)"
                    />
                    <StatCard
                        icon={<CheckCircle color="var(--success)" />}
                        label="Impact (CO2 saved)"
                        value={`${Math.round(stats?.impact?.co2_saved_kg || 0)}kg`}
                        color="var(--success)"
                    />
                </div>

                {/* Dynamic Content */}
                <VolunteerList key={activeTab} type={activeTab} />
            </main>
        </div>
    );
};

const SidebarLink = ({ icon, text, active, onClick }) => (
    <div
        onClick={onClick}
        style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.75rem 1rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            background: active ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
            color: active ? 'var(--primary)' : 'var(--text-main)',
            transition: 'all 0.2s',
            borderLeft: active ? '3px solid var(--primary)' : '3px solid transparent'
        }}
    >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {icon}
            <span style={{ fontSize: '0.925rem', fontWeight: active ? '600' : '400' }}>{text}</span>
        </div>
        <ChevronRight size={14} opacity={active ? 1 : 0} />
    </div>
);

const StatCard = ({ icon, label, value, color }) => (
    <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div style={{
            padding: '1rem',
            borderRadius: '1rem',
            background: `rgba(${color === 'var(--primary)' ? '251, 146, 60' : color === 'var(--secondary)' ? '59, 130, 246' : '34, 197, 94'}, 0.1)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            {icon}
        </div>
        <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{value}</div>
        </div>
    </div>
);

export default Dashboard;
