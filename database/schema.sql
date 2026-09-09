-- QueueWise Database Schema for Supabase / PostgreSQL
-- JP-012 Customer Arrival Queue Simulation & Resource Allocation Optimizer
-- Implements branch state, custom task persistence, and scenario history.

-- ---------------------------------------------------------------------------
-- Branches
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS branches (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Branch Tasks
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS branch_tasks (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    branch_id TEXT NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    task_type TEXT NOT NULL CHECK (task_type IN ('teller', 'loan', 'customer_service')),
    task_name TEXT NOT NULL,
    customers_per_hour NUMERIC NOT NULL CHECK (customers_per_hour >= 0),
    average_service_time_minutes NUMERIC NOT NULL CHECK (average_service_time_minutes > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_branch_tasks_branch_id ON branch_tasks(branch_id);
CREATE INDEX IF NOT EXISTS idx_branch_tasks_task_type ON branch_tasks(task_type);

-- ---------------------------------------------------------------------------
-- Scenario Runs (Snapshots of Baseline, Stress Test, Recovery, What-If)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scenario_runs (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    branch_id TEXT NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    scenario_type TEXT NOT NULL CHECK (scenario_type IN ('baseline', 'stress_test', 'recovery_plan', 'what_if')),
    scenario_name TEXT NOT NULL,
    input_snapshot JSONB NOT NULL,
    result_snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scenario_runs_branch_id ON scenario_runs(branch_id);
CREATE INDEX IF NOT EXISTS idx_scenario_runs_scenario_type ON scenario_runs(scenario_type);
CREATE INDEX IF NOT EXISTS idx_scenario_runs_created_at ON scenario_runs(created_at DESC);

-- ---------------------------------------------------------------------------
-- Seed Default Branch and Canonical Tasks
-- ---------------------------------------------------------------------------
INSERT INTO branches (id, name, location)
VALUES ('branch-main', 'Downtown Main Branch', 'Financial District, Metro Central')
ON CONFLICT (id) DO NOTHING;

INSERT INTO branch_tasks (id, branch_id, task_type, task_name, customers_per_hour, average_service_time_minutes)
VALUES
    ('task-default-1', 'branch-main', 'teller', 'Cash Deposit & Withdrawal', 12.0, 3.5),
    ('task-default-2', 'branch-main', 'teller', 'Bill Pay & Check Cashing', 8.0, 4.0),
    ('task-default-3', 'branch-main', 'loan', 'Personal & Auto Loan Consultation', 3.2, 20.0),
    ('task-default-4', 'branch-main', 'loan', 'Mortgage Pre-Approval Application', 1.6, 25.0),
    ('task-default-5', 'branch-main', 'customer_service', 'Account Opening & Onboarding', 4.5, 12.0),
    ('task-default-6', 'branch-main', 'customer_service', 'Card Replacement & KYC Update', 5.5, 8.0)
ON CONFLICT (id) DO NOTHING;
