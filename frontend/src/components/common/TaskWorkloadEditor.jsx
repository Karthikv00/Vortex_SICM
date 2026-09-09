import React, { useState } from 'react';
import {
  QUEUE_OPTIONS,
  createTask,
  getDefaultServiceMinutes,
  getQueueLabel,
  validateTaskDraft
} from '../../utils/taskModel';

export default function TaskWorkloadEditor({
  tasks = [],
  onChange,
  onSubmit,
  submitting = false,
  submitLabel = 'DETERMINE SCENARIO + ALLOCATE',
  isWhatIf = false,
  title = 'DEFINE CUSTOMER DEMAND',
  subtitle = 'Add the work customers are actually requesting.',
  analysis = null,
  isDirty = false
}) {
  const [selectedQueue, setSelectedQueue] = useState('teller');
  const [taskName, setTaskName] = useState('');
  const [customersPerHour, setCustomersPerHour] = useState('');
  const [serviceMinutes, setServiceMinutes] = useState(String(getDefaultServiceMinutes('teller')));
  const [serviceManuallyEdited, setServiceManuallyEdited] = useState(false);
  const [validationError, setValidationError] = useState('');

  const handleQueueChange = (e) => {
    const nextQueue = e.target.value;
    setSelectedQueue(nextQueue);
    if (!serviceManuallyEdited) {
      setServiceMinutes(String(getDefaultServiceMinutes(nextQueue)));
    }
  };

  const handleServiceChange = (e) => {
    setServiceMinutes(e.target.value);
    setServiceManuallyEdited(true);
  };

  const handleAddTask = (e) => {
    e.preventDefault();
    const draft = {
      taskType: selectedQueue,
      taskName,
      customersPerHour,
      averageServiceTimeMinutes: serviceMinutes
    };

    const err = validateTaskDraft(draft);
    if (err) {
      setValidationError(err);
      return;
    }

    const newTask = createTask(draft);
    onChange?.([...tasks, newTask]);

    // Reset inputs, preserving default for current queue
    setTaskName('');
    setCustomersPerHour('');
    setServiceMinutes(String(getDefaultServiceMinutes(selectedQueue)));
    setServiceManuallyEdited(false);
    setValidationError('');
  };

  const handleRemoveTask = (taskId) => {
    onChange?.(tasks.filter(t => t.id !== taskId));
  };

  const handleSubmit = () => {
    if (!tasks || tasks.length === 0) {
      setValidationError('Add at least one task before determining the scenario and allocating staff.');
      return;
    }
    setValidationError('');
    onSubmit?.(tasks);
  };

  return (
    <div className={`task-workload-editor ${isWhatIf ? 'whatif-editor' : ''}`}>
      <div className="custom-task-intro">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
        <span className="custom-task-count font-mono">{tasks.length} {tasks.length === 1 ? 'TASK' : 'TASKS'} DEFINED</span>
      </div>

      <div className="custom-task-form-panel unified">
        <form className="custom-task-form unified" onSubmit={handleAddTask}>
          <label>
            <span>TASK TYPE / QUEUE</span>
            <select
              className="custom-task-select"
              value={selectedQueue}
              onChange={handleQueueChange}
              aria-label="Select Task Type or Service Queue"
            >
              {QUEUE_OPTIONS.map(q => (
                <option key={q.id} value={q.id}>
                  {q.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>TASK NAME</span>
            <input
              type="text"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
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
              value={customersPerHour}
              onChange={(e) => setCustomersPerHour(e.target.value)}
              placeholder="e.g. 10"
            />
          </label>

          <label>
            <span>AVG SERVICE (MIN)</span>
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={serviceMinutes}
              onChange={handleServiceChange}
              placeholder="e.g. 5.0"
            />
          </label>

          <button className="cmd-btn-primary custom-task-add-btn" type="submit">
            + ADD TASK
          </button>
        </form>
      </div>

      {validationError && (
        <div className="custom-task-validation" role="alert">
          ⚠ {validationError}
        </div>
      )}

      <div className="custom-task-list" aria-live="polite">
        <div className="defined-tasks-header">
          <span className="task-category-kicker">DEFINED TASKS</span>
        </div>

        {tasks.length === 0 ? (
          <div className="custom-task-empty">
            No customer demand tasks defined yet. Add the first task using the form above.
          </div>
        ) : (
          <div className="custom-task-table-wrap">
            <table className="custom-task-table">
              <thead>
                <tr>
                  <th scope="col">TASK TYPE</th>
                  <th scope="col">TASK</th>
                  <th scope="col">CUSTOMERS / HOUR</th>
                  <th scope="col">AVG SERVICE</th>
                  <th scope="col">ACTION</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id}>
                    <td>
                      <span className={`task-type-badge ${task.taskType}`}>
                        {getQueueLabel(task.taskType)}
                      </span>
                    </td>
                    <td><strong>{task.taskName}</strong></td>
                    <td>{task.customersPerHour} / hr</td>
                    <td>{task.averageServiceTimeMinutes} min</td>
                    <td>
                      <button
                        type="button"
                        className="custom-task-remove"
                        onClick={() => handleRemoveTask(task.id)}
                        aria-label={`Remove ${task.taskName}`}
                      >
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

      <div className="custom-task-action-row">
        <div>
          <strong>{isWhatIf ? 'HYPOTHETICAL WORKLOAD' : 'READY TO ALLOCATE?'}</strong>
          <span>
            {isDirty
              ? 'Inputs changed — click allocate to recalculate scenario classification, forecast, and staffing.'
              : tasks.length === 0
              ? 'Add at least one customer demand task to begin simulation.'
              : 'QueueWise automatically determines the scenario (Normal / Peak / Surge) and optimal staffing from defined task volumes.'}
          </span>
        </div>
        <button
          type="button"
          className="cmd-btn-primary custom-task-analyze-btn"
          onClick={handleSubmit}
          disabled={submitting || tasks.length === 0}
        >
          {submitting ? (
            <>
              <span className="btn-spinner" />
              <span>ANALYZING WORKLOAD…</span>
            </>
          ) : (
            submitLabel
          )}
        </button>
      </div>

      {analysis && (
        <div className="custom-task-result">
          <div>
            <span className="task-category-kicker">DETECTED SCENARIO</span>
            <strong className="cyan">{analysis.scenario_label || (analysis.scenario?.scenario_name || '').toUpperCase()}</strong>
          </div>
          <div>
            <span className="task-category-kicker">DEMAND INDEX</span>
            <strong>{analysis.demand_multiplier != null ? `${analysis.demand_multiplier}× normal` : '—'}</strong>
          </div>
          <div>
            <span className="task-category-kicker">RESOURCE PLAN</span>
            <strong className="green">
              {analysis.optimization?.optimized?.allocation?.staff_by_queue ? 'OPTIMIZED' : 'CALCULATED'}
            </strong>
          </div>
        </div>
      )}
    </div>
  );
}
