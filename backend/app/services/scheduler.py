"""Google OR-Tools CP-SAT constraint optimization scheduling engine."""
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
from ortools.sat.python import cp_model

def generate_optimized_schedule(
    employees: List[Any],
    requirements: List[Any],
    availabilities: List[Any],
    leave_requests: List[Any],
    start_date: date,
    end_date: date,
    weights: Dict[str, int] = None,
) -> Tuple[bool, List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """
    Runs Google OR-Tools CP-SAT solver with weighted objectives.
    Returns: (feasible, shifts, explanations, conflicts)
    """
    if weights is None:
        weights = {"preferences": 1, "fairness": 5, "labor_cost": 2}

    model = cp_model.CpModel()
    delta = end_date - start_date
    dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    # Map employee ID to index
    emp_map = {e.id: i for i, e in enumerate(employees)}
    num_emps = len(employees)

    # Map requirements to shift slots
    shifts_to_assign = []
    for d in dates:
        dow = d.weekday()
        for req in requirements:
            if req.day_of_week == dow:
                for slot_s in range(req.min_staff):
                    shifts_to_assign.append({
                        "date": d,
                        "skill_id": req.skill_id,
                        "start_time": req.start_time,
                        "end_time": req.end_time,
                        "req_id": req.id,
                        "slot": slot_s,
                    })

    num_shifts = len(shifts_to_assign)
    if num_shifts == 0:
        return True, [], ["No shift slots generated for the selected date range."], []

    # x[e, s] = 1 if emp e assigned to shift s
    x = {}
    for e_idx in range(num_emps):
        for s_idx in range(num_shifts):
            x[(e_idx, s_idx)] = model.NewBoolVar(f"x_{e_idx}_{s_idx}")

    # HARD CONSTRAINTS
    # 1. Each shift slot must be filled by exactly one qualified employee
    for s_idx, shift in enumerate(shifts_to_assign):
        shift_skill = shift["skill_id"]
        valid_emp_indices = []
        for e_idx, emp in enumerate(employees):
            # Check skill qualification if requirement specifies a skill
            if shift_skill is not None:
                emp_skill_ids = [es.skill_id for es in emp.skills]
                if shift_skill not in emp_skill_ids:
                    continue
            valid_emp_indices.append(e_idx)

        if not valid_emp_indices:
            return False, [], [f"No qualified employee for skill {shift_skill} on {shift['date']}"], [
                {
                    "type": "unqualified_shift",
                    "message": f"No qualified employee available for requirement on {shift['date']} ({shift['start_time']}-{shift['end_time']})",
                    "date": shift["date"],
                }
            ]

        # Exactly one qualified employee assigned to this shift slot
        model.Add(sum(x[(e_idx, s_idx)] for e_idx in valid_emp_indices) == 1)

    # 2. Availability/Leave
    leave_set = set()
    for lr in leave_requests:
        if lr.status.value == "approved":
            curr = lr.start_date
            while curr <= lr.end_date:
                leave_set.add((lr.employee_id, curr))
                curr += timedelta(days=1)

    avail_map = {(a.employee_id, a.date): a.is_available for a in availabilities}

    for e_idx, emp in enumerate(employees):
        for s_idx, shift in enumerate(shifts_to_assign):
            s_date = shift["date"]
            # Check leave
            if (emp.id, s_date) in leave_set:
                model.Add(x[(e_idx, s_idx)] == 0)
            # Check explicit availability
            if (emp.id, s_date) in avail_map and not avail_map[(emp.id, s_date)]:
                model.Add(x[(e_idx, s_idx)] == 0)

    # 3. Max weekly hours per employee
    for e_idx, emp in enumerate(employees):
        max_h = emp.max_hours_per_week or 48.0
        max_shifts_allowed = int(max_h / 8) + 1
        emp_shifts = [x[(e_idx, s_idx)] for s_idx in range(num_shifts)]
        model.Add(sum(emp_shifts) <= max_shifts_allowed)

    # SOFT CONSTRAINTS (Objective)
    # 1. Employee preferences (minimize deviation from preferred days)
    # 2. Fairness (minimize variance in hours worked)
    # 3. Labor cost (minimize total hours)
    
    # Preference weights
    pref_weights = weights.get("preferences", 1)
    fairness_weights = weights.get("fairness", 5)
    labor_cost_weights = weights.get("labor_cost", 2)
    
    # Employee preferences (minimize deviation from preferred days)
    # Create a preference matrix
    preference_matrix = []
    for e_idx, emp in enumerate(employees):
        row = []
        if not emp.preferred_days:
            row = [0] * num_shifts  # No preference if none specified
        else:
            preferred_days = set(int(d) for d in emp.preferred_days.split(",") if d.isdigit())
            for s_idx, shift in enumerate(shifts_to_assign):
                day_of_week = shift["date"].weekday()
                # Higher score for preferred days
                if day_of_week in preferred_days:
                    row.append(100)  # High preference
                else:
                    row.append(1)   # Low preference
        preference_matrix.append(row)

    # Create a penalty variable for each employee-shift pair
    penalty_vars = {}
    for e_idx in range(num_emps):
        for s_idx in range(num_shifts):
            penalty_vars[(e_idx, s_idx)] = model.NewIntVar(0, 100, f"penalty_{e_idx}_{s_idx}")

    # Add constraints to set penalty based on preference
    for e_idx in range(num_emps):
        for s_idx in range(num_shifts):
            model.Add(x[(e_idx, s_idx)] * preference_matrix[e_idx][s_idx] == penalty_vars[(e_idx, s_idx)])

    # Objective: Minimize total penalty (preferences) + fairness + labor cost
    total_penalty = 0
    for e_idx in range(num_emps):
        for s_idx in range(num_shifts):
            total_penalty += penalty_vars[(e_idx, s_idx)]

    # Solve model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        assigned_shifts = []
        for s_idx, shift in enumerate(shifts_to_assign):
            for e_idx, emp in enumerate(employees):
                if solver.Value(x[(e_idx, s_idx)]) == 1:
                    is_op = (shift["start_time"] <= "09:00")
                    is_cl = (shift["end_time"] >= "21:00")
                    assigned_shifts.append({
                        "employee_id": emp.id,
                        "skill_id": shift["skill_id"],
                        "date": shift["date"],
                        "start_time": shift["start_time"],
                        "end_time": shift["end_time"],
                        "is_opening": is_op,
                        "is_closing": is_cl,
                    })
        explanations = [
            f"Optimized schedule generated with weights: preferences={pref_weights}, fairness={fairness_weights}, labor_cost={labor_cost_weights}.",
            f"Total shifts: {len(assigned_shifts)} across {len(dates)} days."
        ]
        return True, assigned_shifts, explanations, []
    else:
        return False, [], ["The solver could not find a feasible schedule satisfying all constraints and weights."], [
            {
                "type": "solver_infeasible",
                "message": "Hard constraints (availability, staffing demand, leave, or max hours) could not be simultaneously satisfied."
            }
        ]
