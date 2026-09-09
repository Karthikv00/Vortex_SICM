import React, { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import BranchOverview from './components/overview/BranchOverview';
import InputDataSummary from './components/overview/InputDataSummary';
import CustomTaskInput from './components/overview/CustomTaskInput';
import GlobalMetricsStrip from './components/overview/GlobalMetricsStrip';
import QueueGrid from './components/queues/QueueGrid';
import DemandForecast from './components/forecast/DemandForecast';
import OverloadAlerts from './components/alerts/OverloadAlerts';
import BaselineAllocation from './components/optimization/BaselineAllocation';
import OptimizedAllocation from './components/optimization/OptimizedAllocation';
import ComparisonMatrix from './components/optimization/ComparisonMatrix';
import WhatIfSimulator from './components/optimization/WhatIfSimulator';
import ExplanationPanel from './components/optimization/ExplanationPanel';
import ErrorState from './components/common/ErrorState';
import { DEFAULT_TASKS } from './utils/taskModel';
import {
  checkHealth,
  getScenario,
  fetchForecast,
  simulateAllocation,
  optimizeScenario,
  simulateWhatIf,
  analyzeCustomWorkload,
  setApiMode
} from './services/api';

export default function App() {
  const [selectedScenario, setSelectedScenario] = useState('normal');
  const [scenarioConfig, setScenarioConfig] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [baselineAllocation, setBaselineAllocation] = useState(null);
  const [baselineResult, setBaselineResult] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [whatIfAllocation, setWhatIfAllocation] = useState(null);

  // Unified canonical workload state
  const [customTasks, setCustomTasks] = useState(DEFAULT_TASKS);
  const [customAnalysis, setCustomAnalysis] = useState(null);
  const [customWorkloadActive, setCustomWorkloadActive] = useState(true);
  const [isDirty, setIsDirty] = useState(false);

  // What-If workload state
  const [whatIfTasks, setWhatIfTasks] = useState(DEFAULT_TASKS);
  const [whatIfAnalysis, setWhatIfAnalysis] = useState(null);
  const [whatIfWorkloadLoading, setWhatIfWorkloadLoading] = useState(false);

  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [customAnalyzing, setCustomAnalyzing] = useState(false);
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState({ online: false, status: 'initializing' });
  const [isLiveApi, setIsLiveApi] = useState(true);
  const [activeNav, setActiveNav] = useState('command-center');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [clock, setClock] = useState(() => new Date().toLocaleTimeString());
  const activeScenarioReqRef = useRef(0);

  useEffect(() => {
    const timer = setInterval(() => setClock(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    checkHealth().then(status => {
      setServerStatus(status);
      if (status.online) {
        setIsLiveApi(true);
        setApiMode(true);
      } else {
        setIsLiveApi(false);
        setApiMode(false);
      }
    });
  }, []);

  const handleAnalyzeCustomWorkload = useCallback(async (tasks) => {
    setCustomAnalyzing(true);
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeCustomWorkload(tasks);
      setCustomAnalysis(result);
      setCustomWorkloadActive(true);
      setSelectedScenario(result.scenario?.scenario_name || 'normal');
      setScenarioConfig(result.scenario);
      setForecast(result.forecast);
      setOptimizationResult(result.optimization);
      setBaselineAllocation(result.optimization?.baseline?.allocation || null);
      setBaselineResult(result.optimization?.baseline?.result || null);
      setWhatIfAllocation(
        result.optimization?.optimized?.allocation?.staff_by_queue ||
        result.optimization?.baseline?.allocation?.staff_by_queue ||
        null
      );
      setWhatIfResult(null);
      setIsDirty(false);
    } catch (err) {
      setError({
        error: 'CUSTOM_WORKLOAD_ERROR',
        message: err.message || 'Could not classify the custom workload or allocate resources.'
      });
    } finally {
      setCustomAnalyzing(false);
      setLoading(false);
    }
  }, []);

  // Initial mount: analyze default tasks through the end-to-end pipeline
  useEffect(() => {
    handleAnalyzeCustomWorkload(DEFAULT_TASKS);
  }, [handleAnalyzeCustomWorkload]);

  const handleCustomTasksChange = (nextTasks) => {
    setCustomTasks(nextTasks);
    setIsDirty(true);
  };

  const handleOptimize = async () => {
    if (!scenarioConfig || !forecast || optimizing) return;
    setOptimizing(true);
    setError(null);
    try {
      const optRes = await optimizeScenario(scenarioConfig, forecast);
      setOptimizationResult(optRes);
      if (optRes.baseline?.result) setBaselineResult(optRes.baseline.result);
      if (optRes.baseline?.allocation) setBaselineAllocation(optRes.baseline.allocation);
      if (optRes.optimized?.allocation?.staff_by_queue) setWhatIfAllocation(optRes.optimized.allocation.staff_by_queue);
    } catch (err) {
      setError({ error: 'OPTIMIZATION_ERROR', message: err.message || 'The mathematical solver encountered an error.' });
    } finally {
      setOptimizing(false);
    }
  };

  const handleRunWhatIfStaffing = async (customStaff) => {
    if (!forecast || !scenarioConfig) return;
    setWhatIfLoading(true);
    try {
      const res = await simulateWhatIf(scenarioConfig, forecast, { label: 'whatif', staff_by_queue: customStaff }, scenarioConfig?.queues);
      setWhatIfResult(res);
      setWhatIfAllocation(customStaff);
    } catch (err) {
      setError({ error: 'WHAT_IF_ERROR', message: err.message || 'What-If simulation failed on backend.' });
    } finally {
      setWhatIfLoading(false);
    }
  };

  const handleRunWhatIfWorkload = async (tasks) => {
    setWhatIfWorkloadLoading(true);
    setError(null);
    try {
      const res = await analyzeCustomWorkload(tasks);
      setWhatIfAnalysis(res);
      if (res.optimization?.optimized?.result) {
        setWhatIfResult(res.optimization.optimized.result);
      }
      if (res.optimization?.optimized?.allocation?.staff_by_queue) {
        setWhatIfAllocation(res.optimization.optimized.allocation.staff_by_queue);
      }
    } catch (err) {
      setError({
        error: 'WHAT_IF_WORKLOAD_ERROR',
        message: err.message || 'What-If workload analysis failed.'
      });
    } finally {
      setWhatIfWorkloadLoading(false);
    }
  };

  const handleApplyWhatIfToLive = () => {
    if (!whatIfAnalysis) return;
    setCustomTasks([...whatIfTasks]);
    setCustomAnalysis(whatIfAnalysis);
    setCustomWorkloadActive(true);
    setSelectedScenario(whatIfAnalysis.scenario?.scenario_name || selectedScenario);
    setScenarioConfig(whatIfAnalysis.scenario);
    setForecast(whatIfAnalysis.forecast);
    setOptimizationResult(whatIfAnalysis.optimization);
    setBaselineAllocation(whatIfAnalysis.optimization?.baseline?.allocation || null);
    setBaselineResult(whatIfAnalysis.optimization?.baseline?.result || null);
    setWhatIfAllocation(whatIfAnalysis.optimization?.optimized?.allocation?.staff_by_queue || null);
    setIsDirty(false);
  };

  const handleNavClick = (navId) => {
    setActiveNav(navId);
    setMobileSidebarOpen(false);
    const targetMap = {
      'command-center': 'header-top',
      queues: 'queues',
      'demand-forecast': 'demand-forecast',
      optimization: 'optimized-allocation',
      simulation: 'simulation',
      'what-if': 'what-if'
    };
    const el = document.getElementById(targetMap[navId]);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const displayScenario = customWorkloadActive && customAnalysis?.scenario?.scenario_name
    ? customAnalysis.scenario.scenario_name
    : selectedScenario;

  return (
    <div className={`vortex-app-root ${mobileSidebarOpen ? 'sidebar-open' : ''}`}>
      <Sidebar
        activeNav={activeNav}
        onNavClick={handleNavClick}
      />
      {mobileSidebarOpen && (
        <div className="mobile-backdrop" onClick={() => setMobileSidebarOpen(false)} />
      )}
      <div className="vortex-main-wrapper" id="header-top">
        <Header
          selectedScenario={displayScenario}
          onOptimize={handleOptimize}
          optimizing={optimizing}
          hasScenario={!!scenarioConfig}
          onMobileToggle={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        />
        <main className="vortex-command-canvas">
          {error && (
            <ErrorState
              error={error}
              onRetry={() => handleAnalyzeCustomWorkload(customTasks)}
            />
          )}
          <BranchOverview
            scenarioConfig={scenarioConfig}
            selectedScenario={displayScenario}
          />
          <InputDataSummary
            scenarioConfig={scenarioConfig}
            forecast={forecast}
          />
          <CustomTaskInput
            tasks={customTasks}
            onChange={handleCustomTasksChange}
            onAnalyze={handleAnalyzeCustomWorkload}
            analyzing={customAnalyzing}
            analysis={customAnalysis}
            isDirty={isDirty}
          />
          <GlobalMetricsStrip
            simulationResult={baselineResult}
            loading={loading}
          />
          <QueueGrid
            queues={scenarioConfig?.queues}
            simulationResult={baselineResult}
            staffAllocation={baselineAllocation?.staff_by_queue || {}}
            loading={loading}
          />
          <DemandForecast
            forecast={forecast}
            scenarioConfig={scenarioConfig}
            selectedScenario={displayScenario}
            loading={loading}
          />
          <OverloadAlerts
            simulationResult={baselineResult}
            selectedScenario={displayScenario}
          />
          <BaselineAllocation
            queues={scenarioConfig?.queues}
            baselineAllocation={baselineAllocation}
            baselineResult={baselineResult}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
          />
          <OptimizedAllocation
            queues={scenarioConfig?.queues}
            baselineAllocation={baselineAllocation}
            optimizedAllocation={optimizationResult?.optimized?.allocation}
            optimizedResult={optimizationResult?.optimized?.result}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
            onRunOptimization={handleOptimize}
            optimizing={optimizing}
          />
          <ExplanationPanel
            optimizationResult={optimizationResult}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
          />
          <ComparisonMatrix
            optimizationResult={optimizationResult}
            baselineResult={baselineResult}
            onOptimizeClick={handleOptimize}
            optimizing={optimizing}
          />
          <WhatIfSimulator
            queues={scenarioConfig?.queues}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
            initialAllocation={whatIfAllocation || baselineAllocation?.staff_by_queue}
            onRunWhatIf={handleRunWhatIfStaffing}
            whatIfResult={whatIfResult}
            loading={whatIfLoading}
            whatIfTasks={whatIfTasks}
            onWhatIfTasksChange={setWhatIfTasks}
            onRunWhatIfWorkload={handleRunWhatIfWorkload}
            whatIfAnalysis={whatIfAnalysis}
            whatIfWorkloadLoading={whatIfWorkloadLoading}
            onApplyWhatIfToLive={handleApplyWhatIfToLive}
          />
        </main>
        <footer className="vortex-footer font-mono">
          <div className="footer-left">
            <span>QUEUEWISE // SEC-OP-012</span>
            <span className="footer-sep">/</span>
            <span>AAVISHKARA-26 HACKATHON</span>
            <span className="footer-sep">/</span>
            <span>DETERMINISTIC SIMULATION & OPTIMIZATION ENGINE</span>
          </div>
          <div className="footer-right">
            <span className="footer-clock cyan">LOCAL TIME: {clock}</span>
            <span className="footer-sep">/</span>
            <span className={`footer-status ${serverStatus?.online ? 'green' : 'critical'}`}>
              SYS STATUS: {serverStatus?.online ? 'ONLINE' : 'LOCAL ENGINE'}
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
