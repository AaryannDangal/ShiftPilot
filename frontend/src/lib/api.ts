const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  businessName: string;
  businessTimezone: string;
  businessCurrency: string;
  userEmail: string;
  userPassword: string;
  userFullName: string;
}

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export async function login(data: LoginRequest): Promise<TokenResponse | null> {
  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function register(data: RegisterRequest): Promise<TokenResponse | null> {
  const res = await fetch(`${API_URL}/api/v1/auth/register`, {
    method: "POST",
    params: new URLSearchParams({
      business_name: data.businessName,
      business_timezone: data.businessTimezone,
      business_currency: data.businessCurrency,
      user_email: data.userEmail,
      user_password: data.userPassword,
      user_full_name: data.userFullName,
    }).toString(),
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  if (!res.ok) return null;
  return res.json();
}

export async function getMe(token: string): Promise<User | null> {
  const res = await fetch(`${API_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  return res.json();
}

export async function apiFetch<T>(url: string, token: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${url}`, {
    ...options,
    headers: {
      ...options?.headers,
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error("API request failed");
  return res.json();
}
