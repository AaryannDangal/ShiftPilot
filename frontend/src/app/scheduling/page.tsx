"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { apiFetch } from "@/lib/api";
import { Schedule, Location, Employee } from "@/types";


export default function SchedulingPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        // Fetch locations
        const locRes = await apiFetch<Location[]>("/api/v1/auth/locations", token);
        setLocations(locRes);

        // Fetch employees
        const empRes = await apiFetch<Employee[]>("/api/v1/employees/", token);
        setEmployees(empRes);

        // Fetch schedules
        const schedRes = await apiFetch<Schedule[]>("/api/v1/scheduling/schedules", token);
        setSchedules(schedRes);
      } catch (err) {
        setError("Failed to load scheduling data.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user]);

  const handleGenerateSchedule = async () => {
    if (!selectedLocationId || !startDate || !endDate) {
      setError("Please select a location and dates.");
      return;
    }

    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const response = await apiFetch<{
        schedule: Schedule | null;
        feasible: boolean;
        conflicts: any[];
        explanations: string[];
      }>(
        "/api/v1/scheduling/generate",
        token,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            location_id: selectedLocationId,
            start_date: startDate,
            end_date: endDate,
            weights: {
              preferences: 1,
              fairness: 5,
              labor_cost: 2
            }
          }),
        }
      );

      if (response.feasible) {
        router.push(`/scheduling/${response.schedule?.id}`);
      } else {
        setError("Schedule generation failed: " + response.conflicts.map(c => c.message).join(", "));
      }
    } catch (err) {
      setError("Failed to generate schedule.");
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-destructive">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Scheduling</h1>
          <p className="text-sm text-muted-foreground">Generate and manage team schedules</p>
        </div>
        <button onClick={logout} className="btn btn-ghost">Sign out</button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Location</label>
            <select
              className="input w-full"
              value={selectedLocationId || ""}
              onChange={(e) => setSelectedLocationId(e.target.value ? parseInt(e.target.value) : null)}
            >
              <option value="" disabled>Select a location</option>
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>{loc.name}</option>
              ))}
            </select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm font-medium">Start Date</label>
              <input
                type="date"
                className="input w-full"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium">End Date</label>
              <input
                type="date"
                className="input w-full"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Generate Schedule</h2>
          <button
            onClick={handleGenerateSchedule}
            className="btn btn-primary"
            disabled={!selectedLocationId || !startDate || !endDate}
          >
            Generate Schedule
          </button>
        </div>

        <div className="border rounded-lg p-4">
          <h3 className="font-medium mb-2">Employees ({employees.length})</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {employees.map((emp) => (
              <div key={emp.id} className="flex justify-between text-sm">
                <span>{emp.full_name}</span>
                <span>{emp.employment_type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
