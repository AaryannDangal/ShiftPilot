"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { Schedule } from "@/types";
import Link from "next/link";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    fetchSchedules();
  }, [user]);

  const fetchSchedules = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(apiUrl + "/api/v1/scheduling/schedules", {
      headers: { Authorization: "Bearer " + token },
    });
    if (res.ok) {
      setSchedules(await res.json());
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Welcome, {user?.full_name}</h1>
          <p className="text-sm text-muted-foreground">Manage your team&apos;s schedule</p>
        </div>
        <button onClick={logout} className="btn btn-ghost">Sign out</button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Link href="/employees" className="block p-6 border rounded-lg hover:shadow-sm">
          <h2 className="text-lg font-semibold">Employees</h2>
          <p className="text-sm text-muted-foreground">Add and manage team members</p>
        </Link>
        <Link href="/scheduling" className="block p-6 border rounded-lg hover:shadow-sm">
          <h2 className="text-lg font-semibold">Scheduling</h2>
          <p className="text-sm text-muted-foreground">Generate and manage schedules</p>
        </Link>
        <Link href="/analytics" className="block p-6 border rounded-lg hover:shadow-sm">
          <h2 className="text-lg font-semibold">Analytics</h2>
          <p className="text-sm text-muted-foreground">View workforce insights</p>
        </Link>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Recent Schedules</h2>
        {schedules.length === 0 ? (
          <p className="text-muted-foreground">No schedules created yet.</p>
        ) : (
          <div className="space-y-4">
            {schedules.map((schedule) => (
              <div key={schedule.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{schedule.start_date} - {schedule.end_date}</h3>
                    <p className="text-sm text-muted-foreground">
                      {schedule.shifts.length} shifts • {schedule.status}
                    </p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-secondary/10 text-secondary">
                    {schedule.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
