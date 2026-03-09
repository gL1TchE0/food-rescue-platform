import React, { useState, useEffect } from 'react';
import { apiService } from '../../api/apiService';
import { Mail, Phone, ExternalLink, ShieldCheck, ShieldX, User, Info } from 'lucide-react';

const VolunteerList = ({ type }) => {
    const [volunteers, setVolunteers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedVolunteer, setSelectedVolunteer] = useState(null);

    const fetchVolunteers = async () => {
        try {
            setLoading(true);
            let res;
            if (type === 'PENDING') res = await apiService.getPendingVolunteers();
            else if (type === 'VERIFIED') res = await apiService.getVerifiedVolunteers();
            else res = await apiService.getRejectedVolunteers();
            setVolunteers(res.data);
        } catch (err) {
            console.error('Failed to fetch volunteers', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVolunteers();
    }, [type]);

    const handleAction = async (id, action, reason) => {
        try {
            if (action === 'approve') await apiService.approveVolunteer(id);
            else await apiService.rejectVolunteer(id, reason);
            setSelectedVolunteer(null);
            fetchVolunteers();
        } catch (err) {
            alert('Action failed: ' + err.message);
        }
    };

    if (loading) return <div style={{ color: 'var(--text-muted)' }}>Fetching list...</div>;

    return (
        <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
                {volunteers.length === 0 ? (
                    <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
                        No volunteers found in this category.
                    </div>
                ) : (
                    volunteers.map(vol => (
                        <div key={vol.id} className="glass-card" style={{ padding: '1.5rem', transition: 'transform 0.2s' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                <div style={{ display: 'flex', gap: '1rem' }}>
                                    <div style={{
                                        width: '48px',
                                        height: '48px',
                                        borderRadius: '12px',
                                        background: 'rgba(255,255,255,0.05)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        <User size={24} color="var(--primary)" />
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.1rem', marginBottom: '0.2rem' }}>{vol.name}</h3>
                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                            {vol.vehicle_type} • {vol.capacity_kg}kg Capacity
                                        </span>
                                    </div>
                                </div>
                                {type === 'PENDING' && <div className="animate-pulse-subtle" style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)' }} />}
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                                    <Mail size={14} color="var(--text-muted)" />
                                    <span style={{ color: 'var(--text-muted)' }}>{vol.email || 'no-email@rescue.org'}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                                    <Phone size={14} color="var(--text-muted)" />
                                    <span style={{ color: 'var(--text-muted)' }}>{vol.phone || '+91 0000000000'}</span>
                                </div>
                            </div>

                            {vol.rejection_reason && (
                                <div style={{
                                    background: 'rgba(239, 68, 68, 0.05)',
                                    padding: '0.75rem',
                                    borderRadius: '0.75rem',
                                    fontSize: '0.8rem',
                                    marginBottom: '1rem',
                                    color: 'var(--error)'
                                }}>
                                    <div style={{ fontWeight: 'bold', marginBottom: '0.2rem' }}>Rejection Reason:</div>
                                    {vol.rejection_reason}
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button
                                    className="btn btn-secondary"
                                    style={{ flex: 1, padding: '0.5rem' }}
                                    onClick={() => setSelectedVolunteer(vol)}
                                >
                                    <Info size={16} />
                                    Details
                                </button>
                                {type === 'PENDING' && (
                                    <button
                                        className="btn btn-primary"
                                        style={{ padding: '0.5rem 1rem' }}
                                        onClick={() => handleAction(vol.id, 'approve')}
                                    >
                                        <ShieldCheck size={16} />
                                        Verify
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Detail Modal */}
            {selectedVolunteer && (
                <div style={{
                    position: 'fixed',
                    inset: 0,
                    background: 'rgba(0,0,0,0.8)',
                    backdropFilter: 'blur(8px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 100,
                    padding: '2rem'
                }}>
                    <div className="glass-card" style={{ width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <div style={{ padding: '2rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                <h2 style={{ fontSize: '1.5rem' }}>Volunteer Details</h2>
                                <button className="btn btn-secondary" style={{ padding: '0.4rem' }} onClick={() => setSelectedVolunteer(null)}>
                                    <XCircle size={18} />
                                </button>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                                <div>
                                    <h4 style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Information</h4>
                                    <p style={{ fontWeight: '600' }}>{selectedVolunteer.name}</p>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{selectedVolunteer.email}</p>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{selectedVolunteer.phone}</p>
                                </div>
                                <div>
                                    <h4 style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Registration</h4>
                                    <p style={{ fontSize: '0.9rem' }}>Joined: {new Date(selectedVolunteer.created_at).toLocaleDateString()}</p>
                                    <p style={{ fontSize: '0.9rem' }}>Capacity: {selectedVolunteer.capacity_kg}kg</p>
                                </div>
                            </div>

                            <div style={{ marginBottom: '2rem' }}>
                                <h4 style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '1rem' }}>ID Proof Document</h4>
                                <div style={{
                                    aspectRatio: '16/9',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: '1rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    border: '2px dashed var(--glass-border)',
                                    overflow: 'hidden'
                                }}>
                                    {selectedVolunteer.id_proof_url ? (
                                        <img src={selectedVolunteer.id_proof_url} alt="ID Proof" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    ) : (
                                        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                            <ShieldX size={48} style={{ marginBottom: '0.5rem', opacity: 0.3 }} />
                                            <p>No document uploaded via mobile yet.</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {type === 'PENDING' && (
                                <div style={{ display: 'flex', gap: '1rem' }}>
                                    <button
                                        className="btn btn-secondary"
                                        style={{ flex: 1, color: 'var(--error)' }}
                                        onClick={() => {
                                            const reason = prompt('Enter rejection reason:');
                                            if (reason) handleAction(selectedVolunteer.id, 'reject', reason);
                                        }}
                                    >
                                        <ShieldX size={18} />
                                        Reject Application
                                    </button>
                                    <button
                                        className="btn btn-primary"
                                        style={{ flex: 2 }}
                                        onClick={() => handleAction(selectedVolunteer.id, 'approve')}
                                    >
                                        <ShieldCheck size={18} />
                                        Approve Volunteer
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const XCircle = ({ size }) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
);

export default VolunteerList;
