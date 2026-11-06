"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { register, getApiBase } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

const TIMEZONES = ["Asia/Kathmandu", "Asia/Kolkata", "Asia/Dubai", "Europe/London", "UTC"]
const CURRENCIES = ["NPR", "INR", "AED", "GBP", "USD"]

export default function RegisterPage() {
  const router = useRouter()
  const { setUser } = useAuth()
  const [businessName, setBusinessName] = useState("")
  const [ownerName, setOwnerName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [timezone, setTimezone] = useState("Asia/Kathmandu")
  const [currency, setCurrency] = useState("NPR")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const apiReady = getApiBase() !== null

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError("")
    setLoading(true)
    try {
      const result = await register({
        businessName,
        businessTimezone: timezone,
        businessCurrency: currency,
        userEmail: email,
        userPassword: password,
        userFullName: ownerName,
      })
      localStorage.setItem("token", result.access_token)
      localStorage.setItem("user", JSON.stringify(result.user))
      setUser(result.user)
      router.push("/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create the account.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="center-screen">
      <div className="auth-card">
        <div className="brand">
          <span className="brand-mark">SP</span>
          <span className="brand-name">ShiftPilot</span>
        </div>
        <div className="card">
          <h1 className="title font-display">Create your account</h1>
          <p className="subtitle">Set up the business and start scheduling in minutes.</p>
          {!apiReady && (
            <p className="warn">
              Backend URL not set. Add NEXT_PUBLIC_API_URL in Vercel pointing at your Render service.
            </p>
          )}
          {error && <p className="error" role="alert">{error}</p>}
          <form onSubmit={onSubmit} className="stack">
            <div className="stack-sm">
              <label className="label" htmlFor="business">Business</label>
              <input id="business" className="input" type="text" placeholder="Restaurant name"
                value={businessName} onChange={(e) => setBusinessName(e.target.value)} required />
            </div>
            <div className="row-2">
              <div className="stack-sm">
                <label className="label" htmlFor="timezone">Timezone</label>
                <select id="timezone" className="input" value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}>
                  {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz}</option>)}
                </select>
              </div>
              <div className="stack-sm">
                <label className="label" htmlFor="currency">Currency</label>
                <select id="currency" className="input" value={currency}
                  onChange={(e) => setCurrency(e.target.value)}>
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <div className="stack-sm">
              <label className="label" htmlFor="owner">Your name</label>
              <input id="owner" className="input" type="text" placeholder="Owner name"
                value={ownerName} onChange={(e) => setOwnerName(e.target.value)} required />
            </div>
            <div className="stack-sm">
              <label className="label" htmlFor="email">Email</label>
              <input id="email" className="input" type="email" autoComplete="email"
                placeholder="you@restaurant.com" value={email}
                onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="stack-sm">
              <label className="label" htmlFor="password">Password</label>
              <input id="password" className="input" type="password" autoComplete="new-password"
                placeholder="At least 8 characters" value={password}
                onChange={(e) => setPassword(e.target.value)} minLength={8} required />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p className="foot">Already have an account? <Link className="link" href="/login">Sign in</Link></p>
        </div>
      </div>
    </main>
  )
}
