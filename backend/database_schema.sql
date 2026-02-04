-- M7 VOLUNTEER LOGISTICS SUBSYSTEM - DATABASE SCHEMA
-- PostgreSQL 15 + PostGIS
-- Version: 1.0.0

-- ENABLE EXTENSIONS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. VOLUNTEERS TABLE
CREATE TABLE volunteers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    vehicle_type VARCHAR(20) CHECK (vehicle_type IN ('BIKE', 'SCOOTER', 'CAR', 'VAN')),
    vehicle_plate VARCHAR(20),
    capacity_kg INT DEFAULT 10,
    status VARCHAR(20) DEFAULT 'OFFLINE', -- ONLINE, BUSY, OFFLINE
    current_location GEOMETRY(POINT, 4326),
    last_heartbeat TIMESTAMP,
    rating NUMERIC(3, 2) DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for spatial queries
CREATE INDEX idx_volunteers_location ON volunteers USING GIST(current_location);
CREATE INDEX idx_volunteers_status ON volunteers(status);
CREATE INDEX idx_volunteers_firebase_uid ON volunteers(firebase_uid);

-- 2. TASKS TABLE
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID NOT NULL,
    ngo_id UUID NOT NULL,
    volunteer_id UUID REFERENCES volunteers(id),
    pickup_location GEOMETRY(POINT, 4326) NOT NULL,
    drop_location GEOMETRY(POINT, 4326) NOT NULL,
    distance_km NUMERIC(5, 2),
    food_type VARCHAR(50),
    expiry_time TIMESTAMP NOT NULL,
    requires_cooling BOOLEAN DEFAULT FALSE,
    status VARCHAR(30) DEFAULT 'PENDING',
    pickup_proof_url VARCHAR(255),
    drop_proof_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes for task queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_volunteer_id ON tasks(volunteer_id);
CREATE INDEX idx_tasks_expiry_time ON tasks(expiry_time);
CREATE INDEX idx_tasks_pickup_location ON tasks USING GIST(pickup_location);
CREATE INDEX idx_tasks_drop_location ON tasks USING GIST(drop_location);

-- 3. TRACKING SESSIONS (Ephemeral)
CREATE TABLE tracking_sessions (
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    volunteer_id UUID REFERENCES volunteers(id),
    mapbox_session_id VARCHAR(100),
    route_polyline TEXT,
    start_time TIMESTAMP DEFAULT NOW(),
    last_update TIMESTAMP,
    PRIMARY KEY (task_id, volunteer_id)
);

CREATE INDEX idx_tracking_task_id ON tracking_sessions(task_id);

-- 4. TASK EXCEPTIONS
CREATE TABLE task_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    issue_type VARCHAR(50), -- FLAT_TIRE, ACCIDENT, FOOD_SPOILED, VEHICLE_ISSUE
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    reported_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE INDEX idx_exceptions_task_id ON task_exceptions(task_id);
CREATE INDEX idx_exceptions_resolved ON task_exceptions(resolved);

-- 5. DONORS TABLE (Added for completeness)
CREATE TABLE donors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    qr_token VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_donors_location ON donors USING GIST(location);
CREATE INDEX idx_donors_qr_token ON donors(qr_token);

-- 6. NGOS TABLE
CREATE TABLE ngos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    qr_token VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ngos_location ON ngos USING GIST(location);
CREATE INDEX idx_ngos_qr_token ON ngos(qr_token);

-- 7. PERFORMANCE STATS (For volunteer ratings)
CREATE TABLE performance_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    volunteer_id UUID REFERENCES volunteers(id),
    task_id UUID REFERENCES tasks(id),
    on_time BOOLEAN,
    completion_time_minutes INT,
    distance_traveled_km NUMERIC(5, 2),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_performance_volunteer_id ON performance_stats(volunteer_id);

-- Helper Function: Find nearby volunteers
CREATE OR REPLACE FUNCTION find_nearby_volunteers(
    pickup_lat NUMERIC,
    pickup_lng NUMERIC,
    max_distance_km NUMERIC DEFAULT 5
)
RETURNS TABLE (
    volunteer_id UUID,
    distance_km NUMERIC,
    vehicle_type VARCHAR,
    rating NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id,
        ST_Distance(
            v.current_location::geography,
            ST_SetSRID(ST_MakePoint(pickup_lng, pickup_lat), 4326)::geography
        ) / 1000 AS distance,
        v.vehicle_type,
        v.rating
    FROM volunteers v
    WHERE v.status = 'ONLINE'
        AND v.current_location IS NOT NULL
        AND ST_DWithin(
            v.current_location::geography,
            ST_SetSRID(ST_MakePoint(pickup_lng, pickup_lat), 4326)::geography,
            max_distance_km * 1000
        )
    ORDER BY distance ASC;
END;
$$ LANGUAGE plpgsql;
