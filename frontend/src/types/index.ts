export interface Employee {
  id: number;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  employment_type: string;
  hourly_wage: number;
  position?: string | null;
  contractual_hours_per_week: number;
  max_hours_per_week: number;
  min_hours_per_week: number;
  max_consecutive_days: number;
  min_rest_hours_between_shifts: number;
  preferred_days?: string | null;
  unavailable_days?: string | null;
  is_active: boolean;
  skills: Skill[];
}

export interface Skill {
  id: number;
  name: string;
  description?: string | null;
}

export interface Shift {
  id: number;
  employee_id: number;
  skill_id?: number | null;
  date: string;
  start_time: string;
  end_time: string;
  is_opening: boolean;
  is_closing: boolean;
}

export interface Schedule {
  id: number;
  location_id: number;
  start_date: string;
  end_date: string;
  status: string;
  shifts: Shift[];
}

export interface Location {
  id: number;
  name: string;
  address?: string | null;
  is_active: boolean;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}
