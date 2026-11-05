"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";

export default function RegisterPage() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [formData, setFormData] = useState({
    businessName: "",
    businessTimezone: "Asia/Kathmandu",
    businessCurrency: "NPR",
    userEmail: "",
    userPassword: "",
    userFullName: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const result = await register(formData);
    if (result) {
      localStorage.setItem("token", result.access_token);
      setUser(result.user);
      router.push("/dashboard");
    } else {
      setError("Registration failed. Please try again.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-lg space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Create your ShiftPilot account</h1>
          <p className="text-sm text-muted-foreground">
            Set up your business and start scheduling in minutes
          </p>
        </div>
        {error && <div className="text-sm text-destructive">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Business</label>
            <input
              type="text"
              placeholder="Restaurant name"
              className="input w-full"
              value={formData.businessName}
              onChange={(e) => setFormData({...formData, businessName: e.target.value})}
              required
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Timezone</label>
              <select
                className="input w-full"
                value={formData.businessTimezone}
                onChange={(e) => setFormData({...formData, businessTimezone: e.target.value})}
              >
                <option value="Asia/Kathmandu">Asia/Kathmandu</option>
                <option value="Asia/Dhaka">Asia/Dhaka</option>
                <option value="Asia/Colombo">Asia/Colombo</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Currency</label>
              <select
                className="input w-full"
                value={formData.businessCurrency}
                onChange={(e) => setFormData({...formData, businessCurrency: e.target.value})}
              >
                <option value="NPR">NPR (NPR)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (EUR)</option>
                <option value="GBP">GBP (GBP)</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Your name</label>
            <input
              type="text"
              placeholder="Owner name"
              className="input w-full"
              value={formData.userFullName}
              onChange={(e) => setFormData({...formData, userFullName: e.target.value})}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Email</label>
            <input
              type="email"
              placeholder="you@restaurant.com"
              className="input w-full"
              value={formData.userEmail}
              onChange={(e) => setFormData({...formData, userEmail: e.target.value})}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Password</label>
            <input
              type="password"
              placeholder="Create a password"
              className="input w-full"
              value={formData.userPassword}
              onChange={(e) => setFormData({...formData, userPassword: e.target.value})}
              required
            />
          </div>
          <button className="btn btn-primary w-full" type="submit">Create account</button>
        </form>
        <p className="text-center text-sm">
          Already have an account? <a href="/login" className="link-primary">Sign in</a>
        </p>
      </div>
    </div>
  );
}
