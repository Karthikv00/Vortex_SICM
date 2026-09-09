import React from 'react';
import TaskWorkloadEditor from '../common/TaskWorkloadEditor';

export default function CustomTaskInput({
  tasks = [],
  onChange,
  onAnalyze,
  analyzing = false,
  analysis = null,
  isDirty = false
}) {
  return (
    <section className="vortex-section custom-task-input-section" id="custom-task-input">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">CUSTOMER DEMAND WORKLOAD</h2>
        <span className="section-sub-tag">AUTO SCENARIO + RESOURCE ALLOCATION</span>
      </div>

      <div className="vortex-card custom-task-card">
        <TaskWorkloadEditor
          tasks={tasks}
          onChange={onChange}
          onSubmit={onAnalyze}
          submitting={analyzing}
          submitLabel="DETERMINE SCENARIO + ALLOCATE"
          isWhatIf={false}
          title="Define the work customers are actually requesting"
          subtitle="Add customer demand tasks across Teller, Loan, and Customer Service. QueueWise aggregates hourly demand, automatically classifies the scenario (Normal, Peak, or Surge), generates the time-slotted forecast, detects overloads, and computes the mathematically optimal staff allocation."
          analysis={analysis}
          isDirty={isDirty}
        />
      </div>
    </section>
  );
}
