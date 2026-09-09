"""
backend/pipeline.py — End-to-end decision pipeline integration for JP-012.

Executes the complete deterministic decision workflow:
  1. Accept a valid ScenarioConfig.
  2. Generate/use corresponding deterministic demand data.
  3. Produce a ForecastResult.
  4. Produce a baseline allocation.
  5. Run the baseline simulation.
  6. Run the optimizer using forecast/simulation inputs and hard constraints.
  7. Run the optimized allocation through the real simulation engine.
  8. Compare baseline vs optimized results using measurable metrics.
  9. Produce the deterministic explanation output.
 10. Return a contract-compatible result suitable for the dashboard/API layer.

Implements: KIRAN-002 (Decision pipeline integration)
Spec:       docs/architecture/api-contract.md
            docs/architecture/data-model.md
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Union

from pydantic import ValidationError

from backend.forecasting.forecast import forecast, validate_forecast
from backend.models import (
    ForecastResult,
    OptimizationResult,
    ScenarioConfig,
)
from backend.optimization.optimizer import optimize

logger = logging.getLogger(__name__)


class DecisionPipelineResult(OptimizationResult):
    """
    Contract-compatible decision pipeline result.

    Subclasses OptimizationResult to maintain exact schema compatibility with
    all downstream API consumers and dashboard components while attaching
    the demand forecast used during the run.
    """

    forecast: Optional[ForecastResult] = None


class DecisionPipeline:
    """
    Deterministic decision workflow pipeline for bank branch operations.

    Orchestrates demand forecasting, baseline allocation, real simulation,
    exhaustive optimization, metric comparison, and explainable recommendations.
    """

    def __init__(
        self,
        scenario: Union[ScenarioConfig, Dict[str, Any]],
        forecast_result: Optional[ForecastResult] = None,
    ) -> None:
        """
        Initialize the decision pipeline.

        Parameters
        ----------
        scenario:
            A validated ScenarioConfig instance or raw dict conforming to ScenarioConfig.
        forecast_result:
            Optional pre-computed ForecastResult. If omitted, the deterministic
            demand forecast is generated from the scenario.
        """
        if isinstance(scenario, dict):
            try:
                self.scenario = ScenarioConfig.model_validate(scenario)
            except ValidationError as e:
                raise ValueError(f"Invalid scenario configuration: {e}") from e
        elif isinstance(scenario, ScenarioConfig):
            self.scenario = scenario
        else:
            raise TypeError(
                f"scenario must be a ScenarioConfig or dict, got {type(scenario).__name__}"
            )

        if forecast_result is not None:
            if not isinstance(forecast_result, ForecastResult):
                raise TypeError(
                    f"forecast_result must be a ForecastResult, got {type(forecast_result).__name__}"
                )
            validate_forecast(self.scenario, forecast_result)
            self.forecast_result = forecast_result
        else:
            # Deterministic demand generation & forecast smoothing
            self.forecast_result = forecast(self.scenario)

    def run(self) -> DecisionPipelineResult:
        """
        Execute the decision pipeline and return the contract-compatible result.

        Returns
        -------
        DecisionPipelineResult (subclass of OptimizationResult)
        """
        logger.info(
            "Running decision pipeline for scenario: %s (seed: %d)",
            self.scenario.scenario_name,
            self.scenario.seed,
        )

        # Optimization runs baseline allocation, baseline simulation,
        # exhaustive candidate simulation, scoring, comparison, and explanation.
        opt_result: OptimizationResult = optimize(self.scenario, self.forecast_result)

        return DecisionPipelineResult(
            scenario_name=opt_result.scenario_name,
            baseline=opt_result.baseline,
            optimized=opt_result.optimized,
            score_breakdown=opt_result.score_breakdown,
            improvement=opt_result.improvement,
            explanation=opt_result.explanation,
            feasible=opt_result.feasible,
            forecast=self.forecast_result,
        )


def run_decision_pipeline(
    scenario: Union[ScenarioConfig, Dict[str, Any]],
    forecast_result: Optional[ForecastResult] = None,
) -> DecisionPipelineResult:
    """
    Convenience function to execute the complete decision pipeline.

    Parameters
    ----------
    scenario:
        ScenarioConfig instance or dictionary.
    forecast_result:
        Optional pre-existing forecast to reuse. If None, forecast is generated.

    Returns
    -------
    DecisionPipelineResult conforming to OptimizationResult.
    """
    pipeline = DecisionPipeline(scenario=scenario, forecast_result=forecast_result)
    return pipeline.run()
