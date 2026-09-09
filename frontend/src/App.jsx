import React, { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import BranchOverview from './components/overview/BranchOverview';
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

import {
  checkHealth,
  getScenario,
  fetchForecast,
  simulateAllocation,
  optimizeScenario,
  simulateWhatIf,
  setApiMode
} from './services/api';

export default function App() {
  const [selectedScenario, setSelectedScenario] = useState('surge'); // Default to surge for high-impact evaluation
  const [scenarioConfig, setScenarioConfig] = useState(null);
  const [forecast, setForecast] = useState(null);
  
  const [baselineAllocation, setBaselineAllocation] = useState(null);
  const [baselineResult, setBaselineResult] = useState(null);
  
  const [optimizationResult, setOptimizationResult] = useState(null);
  
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [whatIfAllocation, setWhatIfAllocation] = useState(null);

  // Status & Loading states
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState({ online: false, status: 'initializing' });
  const [isLiveApi, setIsLiveApi] = useState(true);

  // Navigation state
  const [activeNav, setActiveNav] = useState('command-center');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // Local system clock in footer
  const [clock, setClock] = useState(() => new Date().toLocaleTimeString());

  const activeScenarioReqRef = useRef(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setClock(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Check health on mount
  useEffect(() => {
    checkHealth().then(status => {
      setServerStatus(status);
      if (status.online) {
        setIsLiveApi(true);
        setApiMode(true);
      }
    });
  }, []);

  // Load scenario lifecycle
  const loadScenario = useCallback(async (scName) => {
    const reqId = ++activeScenarioReqRef.current;
    setLoading(true);
    setError(null);
    setOptimizationResult(null); // Clear stale optimization results on scenario change
    setWhatIfResult(null);

    try {
      // 1. Fetch scenario config and authoritative baseline from backend
      const scenarioData = await getScenario(scName);
      if (reqId !== activeScenarioReqRef.current) return;
      const config = scenarioData.scenario || scenarioData;
      setScenarioConfig(config);

      // 2. Fetch forecast
      const fcst = await fetchForecast(config);
      if (reqId !== activeScenarioReqRef.current) return;
      setForecast(fcst);

      // 3. Obtain authoritative baseline allocation directly from backend response
      const basePlan = scenarioData.baseline;
      if (!basePlan) {
        throw new Error('Backend failed to provide authoritative baseline allocation.');
      }
      setBaselineAllocation(basePlan);
      setWhatIfAllocation(basePlan.staff_by_queue);

      // 4. Run baseline simulation with the authoritative baseline
      const baseSim = await simulateAllocation(config, fcst, basePlan);
      if (reqId !== activeScenarioReqRef.current) return;
      setBaselineResult(baseSim);

    } catch (err) {
      if (reqId !== activeScenarioReqRef.current) return;
      console.error('Failed to load scenario:', err);
      setError({
        error: 'SCENARIO_LOAD_FAILURE',
        message: err.message || 'Could not load branch scenario and forecast projections.'
      });
    } finally {
      if (reqId === activeScenarioReqRef.current) {
        setLoading(false);
      }
    }
  }, []);

  // Load selected scenario on change
  useEffect(() => {
    loadScenario(selectedScenario);
  }, [selectedScenario, loadScenario]);

  // Handle Scenario switch from UI: [ NORMAL ] [ PEAK ] [ SURGE ]
  const handleSelectScenario = (scName) => {
    if (scName !== selectedScenario) {
      setSelectedScenario(scName);
    }
  };

  // Run Optimizer CTA
  const handleOptimize = async () => {
    if (!scenarioConfig || !forecast || optimizing) return;
    setOptimizing(true);
    setError(null);

    try {
      const optRes = await optimizeScenario(scenarioConfig, forecast);
      setOptimizationResult(optRes);

      // Set baseline result from optimizer for consistency
      if (optRes.baseline?.result) {
        setBaselineResult(optRes.baseline.result);
      }
      if (optRes.baseline?.allocation) {
        setBaselineAllocation(optRes.baseline.allocation);
      }
      if (optRes.optimized?.allocation?.staff_by_queue) {
        setWhatIfAllocation(optRes.optimized.allocation.staff_by_queue);
      }
    } catch (err) {
      console.error('Optimization failed:', err);
      setError({
        error: 'OPTIMIZATION_ERROR',
        message: err.message || 'The mathematical solver encountered an error while evaluating resource permutations.'
      });
    } finally {
      setOptimizing(false);
    }
  };

  // Run What-If simulation
  const handleRunWhatIf = async (customStaff) => {
    if (!forecast || !scenarioConfig) return;
    setWhatIfLoading(true);
    try {
      const plan = { label: 'whatif', staff_by_queue: customStaff };
      const res = await simulateWhatIf(scenarioConfig, forecast, plan, scenarioConfig?.queues);
      setWhatIfResult(res);
      setWhatIfAllocation(customStaff);
    } catch (err) {
      console.error('What-If simulation failed:', err);
      setError({
        error: 'WHAT_IF_ERROR',
        message: err.message || 'What-If simulation failed on backend.'
      });
    } finally {
      setWhatIfLoading(false);
    }
  };

  // Toggle between real FastAPI and local Mock engine
  const handleToggleApiMode = () => {
    const nextMode = !isLiveApi;
    setIsLiveApi(nextMode);
    setApiMode(nextMode);
    checkHealth().then(status => {
      setServerStatus(status);
      loadScenario(selectedScenario);
    });
  };

  // Sidebar navigation click handler
  const handleNavClick = (navId) => {
    setActiveNav(navId);
    setMobileSidebarOpen(false);

    // Smooth scroll to targeted section
    const targetMap = {
      'command-center': 'header-top',
      'queues': 'queues',
      'demand-forecast': 'demand-forecast',
      'optimization': 'optimized-allocation',
      'simulation': 'simulation',
      'what-if': 'what-if'
    };

    const targetId = targetMap[navId];
    if (targetId) {
      const el = document.getElementById(targetId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  return (
    <div className={`vortex-app-root ${mobileSidebarOpen ? 'sidebar-open' : ''}`}>
      
      {/* 1. LEFT SIDEBAR */}
      <Sidebar
        activeNav={activeNav}
        onNavClick={handleNavClick}
        serverStatus={serverStatus}
        isLiveApi={isLiveApi}
        onToggleApiMode={handleToggleApiMode}
      />

      {/* Mobile Backdrop */}
      {mobileSidebarOpen && (
        <div
          className="mobile-backdrop"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* MAIN COMMAND CENTER WRAPPER */}
      <div className="vortex-main-wrapper" id="header-top">
        
        {/* 1. HEADER */}
        <Header
          selectedScenario={selectedScenario}
          onSelectScenario={handleSelectScenario}
          onOptimize={handleOptimize}
          optimizing={optimizing}
          hasScenario={!!scenarioConfig}
          onMobileToggle={() => setMobileSidebarOpen(!mobileSidebarOpen)}
        />

        {/* Operational Flow Container */}
        <main className="vortex-command-canvas">
          
          {/* Error Banner if Error State Triggered */}
          {error && (
            <ErrorState
              error={error}
              onRetry={() => loadScenario(selectedScenario)}
            />
          )}

          {/* 2. BRANCH OVERVIEW */}
          <BranchOverview
            scenarioConfig={scenarioConfig}
            selectedScenario={selectedScenario}
          />

          {/* 3. GLOBAL OPERATIONAL METRICS */}
          <GlobalMetricsStrip
            simulationResult={baselineResult}
            loading={loading}
          />

          {/* 4. SECTION 1 — CURRENT QUEUES */}
          <QueueGrid
            queues={scenarioConfig?.queues}
            simulationResult={baselineResult}
            staffAllocation={baselineAllocation?.staff_by_queue || {}}
            loading={loading}
          />

          {/* 5. SECTION 2 — DEMAND FORECAST */}
          <DemandForecast
            forecast={forecast}
            scenarioConfig={scenarioConfig}
            selectedScenario={selectedScenario}
            loading={loading}
          />

          {/* 6. SECTION 3 — OVERLOAD ALERTS */}
          <OverloadAlerts
            simulationResult={baselineResult}
            selectedScenario={selectedScenario}
          />

          {/* 7. SECTION 4 — BASELINE ALLOCATION */}
          <BaselineAllocation
            queues={scenarioConfig?.queues}
            baselineAllocation={baselineAllocation}
            baselineResult={baselineResult}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
          />

          {/* 8. SECTION 5 — OPTIMIZED ALLOCATION */}
          <OptimizedAllocation
            queues={scenarioConfig?.queues}
            baselineAllocation={baselineAllocation}
            optimizedAllocation={optimizationResult?.optimized?.allocation}
            optimizedResult={optimizationResult?.optimized?.result}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
            onRunOptimization={handleOptimize}
            optimizing={optimizing}
          />

          {/* 9. SECTION 6 — BEFORE / AFTER COMPARISON (OPTIMIZATION IMPACT) */}
          <ComparisonMatrix
            optimizationResult={optimizationResult}
            baselineResult={baselineResult}
            onOptimizeClick={handleOptimize}
            optimizing={optimizing}
          />

          {/* 10. SECTION 7 — WHAT-IF SIMULATOR */}
          <WhatIfSimulator
            queues={scenarioConfig?.queues}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
            initialAllocation={whatIfAllocation || baselineAllocation?.staff_by_queue}
            onRunWhatIf={handleRunWhatIf}
            whatIfResult={whatIfResult}
            loading={whatIfLoading}
          />

          {/* 11. SECTION 8 — OPTIMIZATION REASONING */}
          <ExplanationPanel
            optimizationResult={optimizationResult}
            totalStaffBudget={scenarioConfig?.total_staff_available || 10}
          />

        </main>

        {/* Tactical Command Deck Footer */}
        <footer className="vortex-footer font-mono">
          <div className="footer-left">
            <span>VORTEX SICM // SEC-OP-012</span>
            <span className="footer-sep">/</span>
            <span>AAVISHKARA-26 HACKATHON</span>
            <span className="footer-sep">/</span>
            <span>DETERMINISTIC SIMULATION & OPTIMIZATION ENGINE</span>
          </div>
          <div className="footer-right">
            <span className="footer-clock cyan">LOCAL TIME: {clock}</span>
            <span className="footer-sep">/</span>
            <span className={`footer-status ${serverStatus?.online ? 'green' : 'critical'}`}>
              SYS STATUS: {serverStatus?.online ? 'ONLINE' : (isLiveApi ? 'OFFLINE' : 'MOCK MODE')}
            </span>
          </div>
        </footer>

      </div>
    </div>
  );
}
