import React, { useMemo, useState } from 'react';

const QUEUE_TYPES = [
  { id: 'teller', label: 'Teller Tasks', description: 'Cash, deposits, withdrawals and counter transactions' },
  { id: 'loans', label: 'Loan Tasks', description: 'Loan enquiries, applications and documentation' },
  { id: 'customer_service', label: 'Customer Service Tasks', description: 'Account support, requests and service issues' }
];

const emptyTask = () => ({ name: '', customers: '', serviceMinutes: '' });

export default function CustomTaskInput({ value = {}, onChange }) {
  const [activeQueue, setActiveQueue] = useState('teller');
  const [draft, setDraft] = useState(emptyTask());
  const [error, setError] = useState('');

  const tasks = useMemo(() => value?.[activeQueue] || [], [value, activeQueue]);

  const updateTasks = (queueId, nextTasks) => {
    onChange?.({ ...value, [queueId]: nextTasks });
  };

  const addTask = (event) => {
    event.preventDefault();
    const name = draft.name.trim();
    const customers = Number(draft.customers);
    const serviceMinutes = Number(draft.serviceMinutes);

    if (!name) return setError('Enter a task name.');
    if (!Number.isFinite(customers) || customers < 0) return setError('Customers must be 0 or greater.');
    if (!Number.isFinite(serviceMinutes) || serviceMinutes <= 0) return setError('Service time must be greater than 0 minutes.');

    updateTasks(activeQueue, [
      ...tasks,
      {
        id: `${activeQueue}-${Date.now()}`,
        name,
        customersPerHour: Math.round(customers),
        serviceMinutes: Math.round(serviceMinutes * 10) / 10
      }
    ]);
    setDraft(emptyTask());
    setError('');
  };

  const removeTask = (taskId) => {
    updateTasks(activeQueue, tasks.filter(task => task.id !== taskId));
  };

  return (
    <section className="vortex-section custom-task-input-section" id="custom-task-input">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">CUSTOM TASK INPUT</h2>
        <span className="section-sub-tag">DEFINE BRANCH WORKLOAD</span>
      </div>

      <div className="vortex-card custom-task-card">
        <div className="custom-task-intro">
          <div>
            <h3>Define the work customers are actually requesting</h3>
            <p>
              Add task types for each service queue. Each task records expected customers per hour and average service time.
              These values define the workload inputs that can be used by the queue model.
            </p>
          </div>
          <span className="custom-task-count">
            {QUEUE_TYPES.reduce((sum, queue) => sum + (value?.[queue.id]?.length || 0), 0)} TASKS DEFINED
          </span>
        </div>

        <div className="task-queue-tabs" role="tablist" aria-label="Service task categories">
          {QUEUE_TYPES.map(queue => (
            <button
              key={queue.id}
              type="button"
              role="tab"
              aria-selected={activeQueue === queue.id}
              className={`task-queue-tab ${activeQueue === queue.id ? 'active' : ''}`}
              onClick={() => { setActiveQueue(queue.id); setDraft(emptyTask()); setError(''); }}
            >
              <strong>{queue.label}</strong>
              <span>{value?.[queue.id]?.length || 0} tasks</span>
            </button>
          ))}
        </div>

        <div className="custom-task-form-panel">
          <div className="custom-task-category-copy">
            <span className="task-category-kicker">CURRENT CATEGORY</span>
            <h4>{QUEUE_TYPES.find(queue => queue.id === activeQueue)?.label}</h4>
            <p>{QUEUE_TYPES.find(queue => queue.id === activeQueue)?.description}</p>
          </div>

          <form className="custom-task-form" onSubmit={addTask}>
            <label>
              <span>TASK NAME</span>
              <input
                type="text"
                value={draft.name}
                onChange={event => setDraft({ ...draft, name: event.target.value })}
                placeholder="e.g. Cash withdrawal"
                maxLength={80}
              />
            </label>
            <label>
              <span>CUSTOMERS / HOUR</span>
              <input
                type="number"
                min="0"
                step="1"
                value={draft.customers}
                onChange={event => setDraft({ ...draft, customers: event.target.value })}
                placeholder="e.g. 24"
              />
            </label>
            <label>
              <span>AVG SERVICE TIME (MIN)</span>
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={draft.serviceMinutes}
                onChange={event => setDraft({ ...draft, serviceMinutes: event.target.value })}
                placeholder="e.g. 4.0"
              />
            </label>
            <button className="cmd-btn-primary custom-task-add-btn" type="submit">+ ADD TASK</button>
          </form>
        </div>

        {error && <div className="custom-task-validation" role="alert">⚠ {error}</div>}

        <div className="custom-task-list" aria-live="polite">
          {tasks.length === 0 ? (
            <div className="custom-task-empty">
              No {QUEUE_TYPES.find(queue => queue.id === activeQueue)?.label.toLowerCase()} defined yet. Add the first task above.
            </div>
          ) : (
            <div className="custom-task-table-wrap">
              <table className="custom-task-table">
                <thead>
                  <tr>
                    <th>TASK</th>
                    <th>CUSTOMERS / HOUR</th>
                    <th>AVG SERVICE</th>
                    <th aria-label="Actions" />
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(task => (
                    <tr key={task.id}>
                      <td>{task.name}</td>
                      <td>{task.customersPerHour}</td>
                      <td>{task.serviceMinutes.toFixed(1)} min</td>
                      <td>
                        <button type="button" className="custom-task-remove" onClick={() => removeTask(task.id)} aria-label={`Remove ${task.name}`}>
                          REMOVE
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
