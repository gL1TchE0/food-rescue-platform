"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { apiService } from "../../../lib/api-service";
import { useWebSocket, WebSocketMessage } from "../../../lib/websocket-service";
import { useToast } from "../../../lib/toast-context";
import { useAuth } from "../../../lib/auth-context";
import dynamic from "next/dynamic";

const DispatcherMap = dynamic(() => import("../../../components/DispatcherMap"), {
    ssr: false,
    loading: () => <div className="w-full h-full flex items-center justify-center bg-slate-900/50 rounded-xl text-slate-400">Loading Map Component...</div>
});

interface Task {
    id: string;
    food_type: string;
    quantity_kg: number;
    status: string;
    pickup_address: string;
    delivery_address?: string;
    volunteer_id?: string;
    created_at: string;
    priority?: number;
    pickup_lat?: number;
    pickup_lng?: number;
    donor_name?: string;
    ngo_id?: string;
    description?: string;
}

interface Volunteer {
    id: string;
    name: string;
    is_available: boolean;
    current_location?: { lat: number; lng: number };
    latitude?: number;
    longitude?: number;
    phone?: string;
    status?: string;
}

export default function DispatcherDashboard() {
    const { user, logout, isAuthenticated, isLoading: authLoading } = useAuth();
    const { addToast } = useToast();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
    const [ngos, setNgos] = useState<any[]>([]);
    const [donors, setDonors] = useState<any[]>([]);

    const [isLoading, setIsLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState<Task | null>(null);
    const [viewMode, setViewMode] = useState<"list" | "map">("list");


    const fetchData = useCallback(async () => {
        // Don't fetch if not authenticated
        const token = localStorage.getItem("auth_token");
        if (!token) {
            setIsLoading(false);
            return;
        }

        try {
            const [tasksRes, volunteersRes, ngosRes, donorsRes] = await Promise.all([
                apiService.getDispatcherTasks(),
                apiService.getVolunteers(),
                apiService.getDispatcherNgos(),
                apiService.getDispatcherDonors(),
            ]);

            if (tasksRes.data) setTasks(tasksRes.data);
            if (volunteersRes.data) setVolunteers(volunteersRes.data);
            if (ngosRes.data) setNgos(ngosRes.data);
            if (donorsRes.data) setDonors(donorsRes.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Real-time updates
    useWebSocket(
        ["task_created", "task_updated", "task_assigned", "task_completed", "volunteer_online", "volunteer_offline"],
        (message: WebSocketMessage) => {
            const typeLabels: Record<string, string> = {
                task_created: "New Task",
                task_updated: "Task Updated",
                task_assigned: "Task Assigned",
                task_completed: "Task Completed",
                volunteer_online: "Volunteer Online",
                volunteer_offline: "Volunteer Offline",
            };

            addToast({
                type: message.type.includes("completed") ? "success" : "info",
                title: typeLabels[message.type] || "Update",
                message: message.payload?.name || message.payload?.food_type || "Real-time update received",
            });

            fetchData();
        },
        [fetchData, addToast] // Include fetchData and addToast in dependencies
    );

    useEffect(() => {
        if (!isAuthenticated || authLoading) return;
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData, isAuthenticated, authLoading]);

    const assignVolunteer = async (taskId: string, volunteerId: string) => {
        const res = await apiService.dispatcherAssignTask(taskId, volunteerId);
        if (!res.error) {
            addToast({ type: "success", title: "Volunteer Assigned", message: "Task has been assigned" });
            fetchData();
            setSelectedTask(null);
        } else {
            addToast({ type: "error", title: "Error", message: res.error });
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "PENDING": return "bg-yellow-500/20 text-yellow-400";
            case "ASSIGNED": return "bg-blue-500/20 text-blue-400";
            case "IN_TRANSIT": return "bg-purple-500/20 text-purple-400";
            case "PICKED_UP": return "bg-[#fb923c]/20 text-[#fb923c]";
            case "COMPLETED": return "bg-green-500/20 text-green-400";
            default: return "bg-slate-500/20 text-slate-400";
        }
    };

    const tasksByStatus = {
        pending: tasks.filter(t => t.status === "PENDING"),
        active: tasks.filter(t => ["ASSIGNED", "IN_TRANSIT", "PICKED_UP"].includes(t.status)),
        completed: tasks.filter(t => t.status === "COMPLETED"),
    };

    return (
        <div className="min-h-screen text-white">
            {/* Background */}
            <div className="fixed inset-0 z-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-[#020617]"></div>
            <div className="bg-nebula-parallax"></div>

            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-50 glass-card rounded-none border-b border-white/10 px-6 py-4">
                <div className="glass-highlight"></div>
                <div className="max-w-[1800px] mx-auto flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-[#fb923c] to-orange-600 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(251,146,60,0.4)]">
                            <span className="material-symbols-outlined text-white">eco</span>
                        </div>
                        <span className="text-xl font-bold">Dispatcher Console</span>
                    </Link>
                    <div className="flex items-center gap-6">
                        <div className="flex bg-slate-800/50 rounded-lg p-1 border border-white/10">
                            <button
                                onClick={() => setViewMode("list")}
                                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${viewMode === "list" ? "bg-[#fb923c] text-slate-900" : "text-slate-400 hover:text-white"
                                    }`}
                            >
                                List View
                            </button>
                            <button
                                onClick={() => setViewMode("map")}
                                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${viewMode === "map" ? "bg-[#fb923c] text-slate-900" : "text-slate-400 hover:text-white"
                                    }`}
                            >
                                Map View
                            </button>
                        </div>

                        {user && (
                            <span className="text-sm text-slate-400">Welcome, {user.full_name || user.name}</span>
                        )}
                        <div className="flex items-center gap-2 text-sm">
                            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                            <span className="text-slate-400">{volunteers.filter(v => v.status === "ONLINE").length} volunteers available</span>
                        </div>
                        <button onClick={logout} className="text-slate-400 hover:text-red-400 transition-colors">
                            <span className="material-symbols-outlined">logout</span>
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="pt-24 px-6 pb-6 relative z-10 max-w-[1800px] mx-auto">
<<<<<<< Updated upstream
                {/* Stats Row */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="glass-card p-4 relative">
                        <div className="glass-highlight"></div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-3xl font-bold text-yellow-400">{tasksByStatus.pending.length}</p>
                                <p className="text-sm text-slate-400">Pending</p>
=======

                {activeTab === "tasks" ? (
                    <>
                        {/* Stats Row */}
                        <div className="grid grid-cols-4 gap-4 mb-6">
                            <div className="glass-card p-4 relative">
                                <div className="glass-highlight"></div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-3xl font-bold text-yellow-400">{tasksByStatus.pending.length}</p>
                                        <p className="text-sm text-slate-400">Pending</p>
                                    </div>
                                    <span className="material-symbols-outlined text-yellow-400 text-3xl opacity-50">pending</span>
                                </div>
                            </div>
                            <div className="glass-card p-4 relative">
                                <div className="glass-highlight"></div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-3xl font-bold text-blue-400">{tasksByStatus.active.length}</p>
                                        <p className="text-sm text-slate-400">Active Tasks</p>
                                    </div>
                                    <span className="material-symbols-outlined text-blue-400 text-3xl opacity-50">local_shipping</span>
                                </div>
                            </div>
                            <div className="glass-card p-4 relative">
                                <div className="glass-highlight"></div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-3xl font-bold text-green-400">{tasksByStatus.completed.length}</p>
                                        <p className="text-sm text-slate-400">Completed Today</p>
                                    </div>
                                    <span className="material-symbols-outlined text-green-400 text-3xl opacity-50">check_circle</span>
                                </div>
                            </div>
                            <div className="glass-card p-4 relative">
                                <div className="glass-highlight"></div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-3xl font-bold text-[#fb923c]">{volunteers.filter(v => v.status === "ONLINE").length}</p>
                                        <p className="text-sm text-slate-400">Available for Assignment</p>
                                    </div>
                                    <span className="material-symbols-outlined text-[#fb923c] text-3xl opacity-50">groups</span>
                                </div>
>>>>>>> Stashed changes
                            </div>
                            <span className="material-symbols-outlined text-yellow-400 text-3xl opacity-50">pending</span>
                        </div>
                    </div>
                    <div className="glass-card p-4 relative">
                        <div className="glass-highlight"></div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-3xl font-bold text-blue-400">{tasksByStatus.active.length}</p>
                                <p className="text-sm text-slate-400">Active</p>
                            </div>
                            <span className="material-symbols-outlined text-blue-400 text-3xl opacity-50">local_shipping</span>
                        </div>
                    </div>
                    <div className="glass-card p-4 relative">
                        <div className="glass-highlight"></div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-3xl font-bold text-green-400">{tasksByStatus.completed.length}</p>
                                <p className="text-sm text-slate-400">Completed Today</p>
                            </div>
                            <span className="material-symbols-outlined text-green-400 text-3xl opacity-50">check_circle</span>
                        </div>
                    </div>
                    <div className="glass-card p-4 relative">
                        <div className="glass-highlight"></div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-3xl font-bold text-[#fb923c]">{volunteers.filter(v => v.is_available).length}</p>
                                <p className="text-sm text-slate-400">Available Volunteers</p>
                            </div>
                            <span className="material-symbols-outlined text-[#fb923c] text-3xl opacity-50">groups</span>
                        </div>
                    </div>
                </div>


                {viewMode === "map" ? (
                    <div className="glass-card p-4 h-[calc(100vh-250px)] relative">
                        <div className="glass-highlight"></div>
                        <DispatcherMap
                            tasks={tasks}
                            volunteers={volunteers}
                            ngos={ngos}
                            donors={donors}
                        />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Task Queue */}
                        <div className="lg:col-span-2 glass-card p-6 relative max-h-[calc(100vh-250px)] overflow-y-auto">
                            <div className="glass-highlight"></div>
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-[#fb923c]">queue</span>
                                Task Queue
                            </h2>

                            {isLoading ? (
                                <div className="flex items-center justify-center py-12">
                                    <div className="w-8 h-8 border-2 border-[#fb923c]/30 border-t-[#fb923c] rounded-full animate-spin"></div>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {tasks.length === 0 ? (
                                        <p className="text-center text-slate-400 py-8">No tasks in queue</p>
                                    ) : (
                                        tasks.map((task) => (
                                            <div
                                                key={task.id}
                                                onClick={() => setSelectedTask(task)}
                                                className={`p-4 bg-slate-800/30 rounded-xl border transition-all cursor-pointer ${selectedTask?.id === task.id ? "border-[#fb923c] bg-[#fb923c]/10" : "border-white/5 hover:border-white/10"
                                                    }`}
                                            >
                                                <div className="flex items-center justify-between mb-2">
                                                    <div className="flex items-center gap-3">
                                                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
                                                            {task.status}
                                                        </span>
                                                        <span className="font-medium">{task.food_type}</span>
                                                    </div>
                                                    <span className="text-lg font-bold text-[#fb923c]">{task.quantity_kg || 0} kg</span>
                                                </div>
                                                <div className="grid grid-cols-2 gap-4 text-sm text-slate-400">
                                                    <div className="flex items-center gap-2">
                                                        <span className="material-symbols-outlined text-green-400 text-sm">location_on</span>
                                                        <span className="truncate">{task.pickup_address}</span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="material-symbols-outlined text-red-400 text-sm">flag</span>
                                                        <span className="truncate">{task.delivery_address || "Awaiting NGO claim"}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Volunteers Panel */}
                        <div className="glass-card p-6 relative max-h-[calc(100vh-250px)] overflow-y-auto">
                            <div className="glass-highlight"></div>
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <span className="material-symbols-outlined text-green-400">groups</span>
                                Volunteers
                            </h2>

                            <div className="space-y-3">
                                {volunteers.map((volunteer) => (
                                    <div
                                        key={volunteer.id}
                                        className={`p-4 rounded-xl border transition-all ${volunteer.is_available
                                            ? "bg-green-500/10 border-green-500/30"
                                            : "bg-slate-800/30 border-white/5"
                                            }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${volunteer.is_available ? "bg-green-500/20" : "bg-slate-700"
                                                    }`}>
                                                    <span className="material-symbols-outlined text-green-400">person</span>
                                                </div>
                                                <div>
                                                    <p className="font-medium">{volunteer.name}</p>
                                                    <p className={`text-xs ${volunteer.is_available ? "text-green-400" : "text-slate-500"}`}>
                                                        {volunteer.is_available ? "Available" : "Busy"}
                                                    </p>
                                                </div>
                                            </div>
                                            {selectedTask && selectedTask.status === "PENDING" && volunteer.is_available && (
                                                <button
                                                    onClick={() => assignVolunteer(selectedTask.id, volunteer.id)}
                                                    className="px-3 py-1 bg-[#fb923c] hover:bg-orange-400 text-slate-900 rounded-lg text-sm font-medium transition-all"
                                                >
                                                    Assign
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
