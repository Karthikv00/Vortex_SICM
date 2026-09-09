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
import { checkHealth, getScenario, fetchForecast, simulateAllocation, optimizeScenario, simulateWhatIf, setApiMode } from './services/api';

const EMPTY_CUSTOM_TASKS = { teller: [], loans: [], customer_service: [] };

export default function App() {
  const [selectedScenario, setSelectedScenario] = useState('surge');
  const [scenarioConfig, setScenarioConfig] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [baselineAllocation, setBaselineAllocation] = useState(null);
  const [baselineResult, setBaselineResult] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [whatIfAllocation, setWhatIfAllocation] = useState(null);
  const [customTasks, setCustomTasks] = useState(EMPTY_CUSTOM_TASKS);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
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
      if (status.online) { setIsLiveApi(true); setApiMode(true); }
      else { setIsLiveApi(false); setApiMode(false); }
    });
  }, []);

  const loadScenario = useCallback(async (scName) => {
    const reqId = ++activeScenarioReqRef.current;
    setLoading(true); setError(null); setOptimizationResult(null); setWhatIfResult(null);
    try {
      const scenarioData = await getScenario(scName);
      if (reqId !== activeScenarioReqRef.current) return;
      const config = scenarioData.scenario || scenarioData;
      setScenarioConfig(config);
      const fcst = await fetchForecast(config);
      if (reqId !== activeScenarioReqRef.current) return;
      setForecast(fcst);
      const basePlan = scenarioData.baseline;
      if (!basePlan) throw new Error('Backend failed to provide authoritative baseline allocation.');
      setBaselineAllocation(basePlan); setWhatIfAllocation(basePlan.staff_by_queue);
      const baseSim = await simulateAllocation(config, fcst, basePlan);
      if (reqId !== activeScenarioReqRef.current) return;
      setBaselineResult(baseSim);
    } catch (err) {
      if (reqId !== activeScenarioReqRef.current) return;
      setError({ error: 'SCENARIO_LOAD_FAILURE', message: err.message || 'Could not load branch scenario and forecast projections.' });
    } finally { if (reqId === activeScenarioReqRef.current) setLoading(false); }
  }, []);

  useEffect(() => { loadScenario(selectedScenario); }, [selectedScenario, loadScenario]);
  const handleSelectScenario = scName => { if (scName !== selectedScenario) setSelectedScenario(scName); };

  const handleOptimize = async () => {
    if (!scenarioConfig || !forecast || optimizing) return;
    setOptimizing(true); setError(null);
    try {
      const optRes = await optimizeScenario(scenarioConfig, forecast);
      setOptimizationResult(optRes);
      if (optRes.baseline?.result) setBaselineResult(optRes.baseline.result);
      if (optRes.baseline?.allocation) setBaselineAllocation(optRes.baseline.allocation);
      if (optRes.optimized?.allocation?.staff_by_queue) setWhatIfAllocation(optRes.optimized.allocation.staff_by_queue);
    } catch (err) {
      setError({ error: 'OPTIMIZATION_ERROR', message: err.message || 'The mathematical solver encountered an error.' });
    } finally { setOptimizing(false); }
  };

  const handleRunWhatIf = async customStaff => {
    if (!forecast || !scenarioConfig) return;
    setWhatIfLoading(true);
    try {
      const res = await simulateWhatIf(scenarioConfig, forecast, { label: 'whatif', staff_by_queue: customStaff }, scenarioConfig?.queues);
      setWhatIfResult(res); setWhatIfAllocation(customStaff);
    } catch (err) {
      setError({ error: 'WHAT_IF_ERROR', message: err.message || 'What-If simulation failed on backend.' });
    } finally { setWhatIfLoading(false); }
  };

  const handleNavClick = navId => {
    setActiveNav(navId); setMobileSidebarOpen(false);
    const targetMap = { 'command-center': 'header-top', queues: 'queues', 'demand-forecast': 'demand-forecast', optimization: 'optimized-allocation', simulation: 'simulation', 'what-if': 'what-if' };
    const el = document.getElementById(targetMap[navId]);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className={`vortex-app-root ${mobileSidebarOpen ? 'sidebar-open' : ''}`}>
      <Sidebar activeNav={activeNav} onNavClick={handleNavClick} serverStatus={serverStatus} isLiveApi={isLiveApi} />
      {mobileSidebarOpen && <div className="mobile-backdrop" onClick={() => setMobileSidebarOpen(false)} />}
      <div className="vortex-main-wrapper" id="header-top">
        <Header selectedScenario={selectedScenario} onSelectScenario={handleSelectScenario} onOptimize={handleOptimize} optimizing={optimizing} hasScenario={!!scenarioConfig} onMobileToggle={() => setMobileSidebarOpen(!mobileSidebarOpen)} />
        <main className="vortex-command-canvas">
          {error && <ErrorState error={error} onRetry={() => loadScenario(selectedScenario)} />}
          <BranchOverview scenarioConfig={scenarioConfig} selectedScenario={selectedScenario} />
          <InputDataSummary scenarioConfig={scenarioConfig} forecast={forecast} selectedScenario={selectedScenario} customTasks={customTasks} />
          <CustomTaskInput value={customTasks} onChange={setCustomTasks} />
          <GlobalMetricsStrip simulationResult={baselineResult} loading={loading} />
          <QueueGrid queues={scenarioConfig?.queues} simulationResult={baselineResult} staffAllocation={baselineAllocation?.staff_by_queue || {}} loading={loading} />
          <DemandForecast forecast={forecast} scenarioConfig={scenarioConfig} selectedScenario={selectedScenario} loading={loading} />
          <OverloadAlerts simulationResult={baselineResult} selectedScenario={selectedScenario} />
          <BaselineAllocation queues={scenarioConfig?.queues} baselineAllocation={baselineAllocation} baselineResult={baselineResult} totalStaffBudget={scenarioConfig?.total_staff_available || 10} />
          <OptimizedAllocation queues={scenarioConfig?.queues} baselineAllocation={baselineAllocation} optimizedAllocation={optimizationResult?.optimized?.allocation} optimizedResult={optimizationResult?.optimized?.result} totalStaffBudget={scenarioConfig?.total_staff_available || 10} onRunOptimization={handleOptimize} optimizing={optimizing} />
          <ExplanationPanel optimizationResult={optimizationResult} totalStaffBudget={scenarioConfig?.total_staff_available || 10} />
          <ComparisonMatrix optimizationResult={optimizationResult} baselineResult={baselineResult} onOptimizeClick={handleOptimize} optimizing={optimizing} />
          <WhatIfSimulator queues={scenarioConfig?.queues} totalStaffBudget={scenarioConfig?.total_staff_available || 10} initialAllocation={whatIfAllocation || baselineAllocation?.staff_by_queue} onRunWhatIf={handleRunWhatIf} whatIfResult={whatIfResult} loading={whatIfLoading} />
        </main>
        <footer className="vortex-footer font-mono"><div className="footer-left"><span>QUEUEWISE // SEC-OP-012</span><span className="footer-sep">/</span><span>AAVISHKARA-26 HACKATHON</span><span className="footer-sep">/</span><span>DETERMINISTIC SIMULATION & OPTIMIZATION ENGINE</span></div><div className="footer-right"><span className="footer-clock cyan">LOCAL TIME: {clock}</span><span className="footer-sep">/</span><span className={`footer-status ${serverStatus?.online ? 'green' : 'critical'}`}>SYS STATUS: {serverStatus?.online ? 'ONLINE' : 'LOCAL ENGINE'}</span></div></footer>
      </div>
    </div>
  );
}
