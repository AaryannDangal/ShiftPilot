const API_MISSING =
  "Backend URL is not configured. Set NEXT_PUBLIC_API_URL in Vercel to your Render service URL."

export function getApiBase(): string | null {
  const value = process.env.NEXT_PUBLIC_API_URL
  if (!value || !value.trim()) return null
  return value.trim().replace(/\/+$/, "")
}

interface LoginRequest { email: string; password: string }
interface RegisterRequest {
  businessName: string
  businessTimezone: string
  businessCurrency: string
  userEmail: string
  userPassword: string
  userFullName: string
}
interface User { id: number; email: string; full_name: string; role: string; is_active: boolean }
interface TokenResponse { access_token: string; token_type: string; user: User }

async function handle(res: Response): Promise<any> {
  if (res.ok) return res.json()
  let detail = `Request failed (${res.status})`
  const text = await res.text()
  try {
    const parsed = JSON.parse(text)
    if (parsed && typeof parsed.detail === "string") detail = parsed.detail
  } catch {
    detail = text || detail
  }
  throw new Error(detail)
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const base = getApiBase()
  if (!base) throw new Error(API_MISSING)
  const res = await fetch(`${base}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  return handle(res)
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const base = getApiBase()
  if (!base) throw new Error(API_MISSING)
  const params = new URLSearchParams({
    business_name: data.businessName,
    business_timezone: data.businessTimezone,
    business_currency: data.businessCurrency,
    user_email: data.userEmail,
    user_password: data.userPassword,
    user_full_name: data.userFullName,
  })
  const res = await fetch(`${base}/api/v1/auth/register?${params.toString()}`, { method: "POST" })
  return handle(res)
}

export async function getMe(token: string): Promise<User> {
  const base = getApiBase()
  if (!base) throw new Error(API_MISSING)
  const res = await fetch(`${base}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
  return handle(res)
}

export async function apiFetch<T>(url: string, token: string, options?: RequestInit): Promise<T> {
  const base = getApiBase()
  if (!base) throw new Error(API_MISSING)
  const res = await fetch(`${base}${url}`, {
    ...options,
    headers: { ...(options?.headers || {}), Authorization: `Bearer ${token}` },
  })
  return handle(res) as Promise<T>
}
