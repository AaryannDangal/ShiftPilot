"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { login, getApiBase } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const apiReady = getApiBase() !== null

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError("")
    setLoading(true)
    try {
      const result = await login({ email, password })
      localStorage.setItem("token", result.access_token)
      localStorage.setItem("user", JSON.stringify(result.user))
      setUser(result.user)
      router.push("/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.")
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
          <h1 className="title font-display">Sign in</h1>
          <p className="subtitle">Open your workspace to plan the week ahead.</p>
          {!apiReady && (
            <p className="warn">
              Backend URL not set. Add NEXT_PUBLIC_API_URL in Vercel pointing at your Render service.
            </p>
          )}
          {error && <p className="error" role="alert">{error}</p>}
          <form onSubmit={onSubmit} className="stack">
            <div className="stack-sm">
              <label className="label" htmlFor="email">Email</label>
              <input id="email" className="input" type="email" autoComplete="email"
                placeholder="owner@restaurant.com" value={email}
                onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="stack-sm">
              <label className="label" htmlFor="password">Password</label>
              <input id="password" className="input" type="password" autoComplete="current-password"
                placeholder="Your password" value={password}
                onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="foot">New here? <Link className="link" href="/register">Create an account</Link></p>
        </div>
      </div>
    </main>
  )
}
