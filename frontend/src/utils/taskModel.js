/**
 * frontend/src/utils/taskModel.js
 *
 * Canonical task data model and normalization helpers for QueueWise.
 * Shared across the main workload input, backend API client, and What-If Simulator.
 */

export const QUEUE_OPTIONS = [
  { id: 'teller', label: 'Teller', defaultServiceMinutes: 5 },
  { id: 'loans', label: 'Loan', defaultServiceMinutes: 20 },
  { id: 'customer_service', label: 'Customer Service', defaultServiceMinutes: 8 }
];

export const DEFAULT_TASKS = [
  {
    id: 'task-default-1',
    taskType: 'teller',
    taskName: 'Cash withdrawal',
    customersPerHour: 20,
    averageServiceTimeMinutes: 4
  },
  {
    id: 'task-default-2',
    taskType: 'loans',
    taskName: 'Loan enquiries',
    customersPerHour: 5,
    averageServiceTimeMinutes: 15
  },
  {
    id: 'task-default-3',
    taskType: 'customer_service',
    taskName: 'Account services',
    customersPerHour: 10,
    averageServiceTimeMinutes: 8
  }
];

export function getQueueLabel(queueId) {
  const norm = queueId === 'loan' ? 'loans' : queueId;
  const match = QUEUE_OPTIONS.find(q => q.id === norm);
  return match?.label || queueId;
}

export function getDefaultServiceMinutes(queueId) {
  const norm = queueId === 'loan' ? 'loans' : queueId;
  const match = QUEUE_OPTIONS.find(q => q.id === norm);
  return match?.defaultServiceMinutes ?? 5;
}

export function createTask({ taskType = 'teller', taskName = '', customersPerHour = '', averageServiceTimeMinutes = '' }) {
  const normalizedType = taskType === 'loan' ? 'loans' : taskType;
  return {
    id: `task-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    taskType: normalizedType,
    taskName: taskName.trim(),
    customersPerHour: Math.max(0, Math.round(Number(customersPerHour) || 0)),
    averageServiceTimeMinutes: Math.max(0.1, Math.round((Number(averageServiceTimeMinutes) || getDefaultServiceMinutes(normalizedType)) * 10) / 10)
  };
}

export function validateTaskDraft(draft) {
  if (!draft.taskName || !draft.taskName.trim()) {
    return 'Enter a task name.';
  }
  const customers = Number(draft.customersPerHour);
  if (!Number.isFinite(customers) || customers < 0) {
    return 'Customers per hour must be 0 or greater.';
  }
  const service = Number(draft.averageServiceTimeMinutes);
  if (!Number.isFinite(service) || service <= 0) {
    return 'Service time must be greater than 0 minutes.';
  }
  return null;
}

export function normalizeTasksForApi(tasks = [], seed = 42) {
  const taskList = Array.isArray(tasks) ? tasks : [];
  const teller = [];
  const loans = [];
  const customer_service = [];

  const unifiedList = taskList.map(t => {
    const rawType = t.taskType || t.queueId || 'teller';
    const queueId = rawType === 'loan' ? 'loans' : rawType;
    const name = (t.taskName || t.name || '').trim();
    const customers = Number(t.customersPerHour ?? t.customers_per_hour ?? 0);
    const service = Number(t.averageServiceTimeMinutes ?? t.serviceMinutes ?? t.service_minutes ?? getDefaultServiceMinutes(queueId));

    const item = {
      name,
      customers_per_hour: customers,
      service_minutes: service
    };

    if (queueId === 'teller') teller.push(item);
    else if (queueId === 'loans') loans.push(item);
    else if (queueId === 'customer_service') customer_service.push(item);

    return {
      task_type: queueId,
      name,
      customers_per_hour: customers,
      service_minutes: service
    };
  });

  return {
    tasks: unifiedList,
    teller,
    loans,
    customer_service,
    seed
  };
}
