/**
 * frontend/src/mocks/mockData.js
 * 
 * Strict implementation of docs/architecture/data-model.md & backend/models.py.
 * Provides deterministic data for 'normal', 'peak', and 'surge' scenarios.
 */

// 32 slots from 09:00 to 17:00 (15-min increments)
export const TIME_SLOTS = [
  "09:00", "09:15", "09:30", "09:45",
  "10:00", "10:15", "10:30", "10:45",
  "11:00", "11:15", "11:30", "11:45",
  "12:00", "12:15", "12:30", "12:45",
  "13:00", "13:15", "13:30", "13:45",
  "14:00", "14:15", "14:30", "14:45",
  "15:00", "15:15", "15:30", "15:45",
  "16:00", "16:15", "16:30", "16:45"
];

export const QUEUES_CONFIG = [
  { queue_id: "teller", name: "Teller Service", min_staff: 1, max_staff: 6, avg_service_time_minutes: 4.0 },
  { queue_id: "loans", name: "Loans & Mortgages", min_staff: 1, max_staff: 3, avg_service_time_minutes: 15.0 },
  { queue_id: "customer_service", name: "Customer Service", min_staff: 1, max_staff: 4, avg_service_time_minutes: 8.0 },
  { queue_id: "cashier", name: "Cashier / Commercial", min_staff: 1, max_staff: 4, avg_service_time_minutes: 3.5 }
];

export const SCENARIOS = {
  surge: {
    scenario_name: "surge",
    seed: 42,
    horizon_start: "09:00",
    horizon_end: "17:00",
    slot_minutes: 15,
    total_staff_available: 10,
    queues: QUEUES_CONFIG,
    forecast: {
      scenario_name: "surge",
      slots: TIME_SLOTS,
      expected_arrivals: {
        // Surge in 11:00 to 13:30 window (slots 8 to 17)
        teller: [
          4, 5, 6, 7,  8, 9, 11, 13,
          18, 22, 25, 24, 21, 19, 16, 14,
          12, 10, 8, 7,  6, 5, 5, 4,
          4, 3, 3, 2,  2, 2, 1, 1
        ],
        loans: [
          1, 1, 1, 1,  2, 2, 2, 2,
          3, 3, 4, 3,  3, 2, 2, 2,
          2, 1, 1, 1,  1, 1, 1, 1,
          1, 0, 0, 0,  0, 0, 0, 0
        ],
        customer_service: [
          2, 2, 3, 3,  4, 4, 5, 6,
          7, 8, 9, 8,  7, 6, 5, 4,
          4, 3, 3, 3,  2, 2, 2, 2,
          1, 1, 1, 1,  1, 0, 0, 0
        ],
        cashier: [
          3, 3, 4, 5,  6, 7, 8, 9,
          12, 14, 15, 13, 11, 9, 8, 6,
          5, 4, 4, 3,  3, 3, 2, 2,
          2, 1, 1, 1,  1, 1, 0, 0
        ]
      }
    },
    baseline: {
      allocation: {
        label: "baseline",
        staff_by_queue: { teller: 4, loans: 2, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "baseline",
        per_queue: {
          teller: {
            avg_wait_minutes: 11.4,
            p95_wait_minutes: 24.8,
            utilization: 0.94,
            overloaded_slots: ["11:00", "11:15", "11:30", "11:45", "12:00", "12:15"],
            total_served: 286,
            end_backlog: 18
          },
          loans: {
            avg_wait_minutes: 4.8,
            p95_wait_minutes: 12.0,
            utilization: 0.48,
            overloaded_slots: [],
            total_served: 42,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 8.2,
            p95_wait_minutes: 18.5,
            utilization: 0.82,
            overloaded_slots: ["11:30", "11:45"],
            total_served: 98,
            end_backlog: 4
          },
          cashier: {
            avg_wait_minutes: 3.2,
            p95_wait_minutes: 7.5,
            utilization: 0.65,
            overloaded_slots: [],
            total_served: 142,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 8.4,
          p95_wait_minutes: 21.2,
          overloaded_slot_count: 8,
          total_served: 568,
          total_end_backlog: 22
        }
      },
      score: 54.2
    },
    optimized: {
      allocation: {
        label: "optimized",
        staff_by_queue: { teller: 5, loans: 1, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "optimized",
        per_queue: {
          teller: {
            avg_wait_minutes: 5.4,
            p95_wait_minutes: 13.2,
            utilization: 0.78,
            overloaded_slots: ["11:30"],
            total_served: 302,
            end_backlog: 2
          },
          loans: {
            avg_wait_minutes: 6.9,
            p95_wait_minutes: 15.1,
            utilization: 0.72,
            overloaded_slots: [],
            total_served: 42,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 7.9,
            p95_wait_minutes: 16.8,
            utilization: 0.81,
            overloaded_slots: ["11:30"],
            total_served: 100,
            end_backlog: 2
          },
          cashier: {
            avg_wait_minutes: 3.2,
            p95_wait_minutes: 7.5,
            utilization: 0.65,
            overloaded_slots: [],
            total_served: 142,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 5.1,
          p95_wait_minutes: 12.8,
          overloaded_slot_count: 2,
          total_served: 586,
          total_end_backlog: 4
        }
      },
      score: 83.6
    },
    score_breakdown: {
      wait_score: 31.8,
      overload_score: 35.0,
      utilization_score: 18.8,
      reallocation_cost: -2.0,
      total_score: 83.6
    },
    improvement: {
      avg_wait_reduction_minutes: 3.3,
      p95_wait_reduction_minutes: 8.4,
      overloaded_slots_resolved: 6,
      utilization_delta: 0.08
    },
    explanation: "Demand surges intensely at Teller counters (+140% above baseline) between 11:00 and 13:30. In contrast, Loan inquiries remain stable with low staff utilization (48%). Reallocating 1 specialist from Loans to Teller relieves 6 bottleneck slots, cuts branch-wide average customer wait from 8.4 min to 5.1 min (-39%), and maintains all service constraints (min 1 per queue, 10 total staff).",
    feasible: true
  },

  peak: {
    scenario_name: "peak",
    seed: 42,
    horizon_start: "09:00",
    horizon_end: "17:00",
    slot_minutes: 15,
    total_staff_available: 10,
    queues: QUEUES_CONFIG,
    forecast: {
      scenario_name: "peak",
      slots: TIME_SLOTS,
      expected_arrivals: {
        teller: [
          3, 4, 5, 6,  7, 8, 9, 10,
          13, 15, 16, 15, 13, 12, 10, 8,
          7, 6, 5, 4,  4, 3, 3, 2,
          2, 2, 2, 1,  1, 1, 1, 0
        ],
        loans: [
          1, 1, 1, 1,  2, 2, 2, 2,
          2, 2, 3, 2,  2, 2, 1, 1,
          1, 1, 1, 1,  1, 0, 0, 0,
          0, 0, 0, 0,  0, 0, 0, 0
        ],
        customer_service: [
          2, 2, 2, 3,  3, 4, 4, 5,
          5, 6, 6, 5,  4, 4, 3, 3,
          2, 2, 2, 2,  1, 1, 1, 1,
          1, 0, 0, 0,  0, 0, 0, 0
        ],
        cashier: [
          2, 3, 3, 4,  5, 5, 6, 7,
          8, 9, 10, 9,  8, 7, 5, 4,
          4, 3, 3, 2,  2, 2, 1, 1,
          1, 1, 0, 0,  0, 0, 0, 0
        ]
      }
    },
    baseline: {
      allocation: {
        label: "baseline",
        staff_by_queue: { teller: 4, loans: 2, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "baseline",
        per_queue: {
          teller: {
            avg_wait_minutes: 7.2,
            p95_wait_minutes: 16.4,
            utilization: 0.83,
            overloaded_slots: ["11:15", "11:30"],
            total_served: 218,
            end_backlog: 4
          },
          loans: {
            avg_wait_minutes: 3.5,
            p95_wait_minutes: 8.2,
            utilization: 0.42,
            overloaded_slots: [],
            total_served: 34,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 5.6,
            p95_wait_minutes: 12.8,
            utilization: 0.69,
            overloaded_slots: [],
            total_served: 76,
            end_backlog: 0
          },
          cashier: {
            avg_wait_minutes: 2.8,
            p95_wait_minutes: 6.4,
            utilization: 0.58,
            overloaded_slots: [],
            total_served: 112,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 5.8,
          p95_wait_minutes: 14.1,
          overloaded_slot_count: 2,
          total_served: 440,
          total_end_backlog: 4
        }
      },
      score: 68.4
    },
    optimized: {
      allocation: {
        label: "optimized",
        staff_by_queue: { teller: 5, loans: 1, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "optimized",
        per_queue: {
          teller: {
            avg_wait_minutes: 4.1,
            p95_wait_minutes: 9.8,
            utilization: 0.68,
            overloaded_slots: [],
            total_served: 222,
            end_backlog: 0
          },
          loans: {
            avg_wait_minutes: 5.4,
            p95_wait_minutes: 11.6,
            utilization: 0.62,
            overloaded_slots: [],
            total_served: 34,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 5.6,
            p95_wait_minutes: 12.8,
            utilization: 0.69,
            overloaded_slots: [],
            total_served: 76,
            end_backlog: 0
          },
          cashier: {
            avg_wait_minutes: 2.8,
            p95_wait_minutes: 6.4,
            utilization: 0.58,
            overloaded_slots: [],
            total_served: 112,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 4.2,
          p95_wait_minutes: 9.9,
          overloaded_slot_count: 0,
          total_served: 444,
          total_end_backlog: 0
        }
      },
      score: 89.2
    },
    score_breakdown: {
      wait_score: 34.5,
      overload_score: 40.0,
      utilization_score: 16.7,
      reallocation_cost: -2.0,
      total_score: 89.2
    },
    improvement: {
      avg_wait_reduction_minutes: 1.6,
      p95_wait_reduction_minutes: 4.2,
      overloaded_slots_resolved: 2,
      utilization_delta: 0.05
    },
    explanation: "During peak midday hours, Teller encounters a temporary bottleneck resulting in 2 overloaded slots. Shifting 1 resource from Loans to Teller completely eliminates all queue overloads and reduces average wait by 1.6 minutes without penalizing Loan customer service.",
    feasible: true
  },

  normal: {
    scenario_name: "normal",
    seed: 42,
    horizon_start: "09:00",
    horizon_end: "17:00",
    slot_minutes: 15,
    total_staff_available: 10,
    queues: QUEUES_CONFIG,
    forecast: {
      scenario_name: "normal",
      slots: TIME_SLOTS,
      expected_arrivals: {
        teller: [
          2, 3, 3, 4,  4, 5, 5, 6,
          7, 8, 8, 7,  6, 5, 5, 4,
          4, 3, 3, 3,  2, 2, 2, 1,
          1, 1, 1, 1,  0, 0, 0, 0
        ],
        loans: [
          1, 1, 1, 1,  1, 1, 1, 1,
          2, 2, 2, 1,  1, 1, 1, 1,
          1, 1, 0, 0,  0, 0, 0, 0,
          0, 0, 0, 0,  0, 0, 0, 0
        ],
        customer_service: [
          1, 1, 2, 2,  2, 3, 3, 3,
          4, 4, 4, 3,  3, 2, 2, 2,
          2, 1, 1, 1,  1, 1, 0, 0,
          0, 0, 0, 0,  0, 0, 0, 0
        ],
        cashier: [
          2, 2, 2, 3,  3, 4, 4, 5,
          5, 6, 6, 5,  4, 4, 3, 3,
          2, 2, 2, 1,  1, 1, 1, 0,
          0, 0, 0, 0,  0, 0, 0, 0
        ]
      }
    },
    baseline: {
      allocation: {
        label: "baseline",
        staff_by_queue: { teller: 4, loans: 2, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "baseline",
        per_queue: {
          teller: {
            avg_wait_minutes: 3.1,
            p95_wait_minutes: 6.8,
            utilization: 0.52,
            overloaded_slots: [],
            total_served: 112,
            end_backlog: 0
          },
          loans: {
            avg_wait_minutes: 2.1,
            p95_wait_minutes: 4.5,
            utilization: 0.28,
            overloaded_slots: [],
            total_served: 20,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 3.4,
            p95_wait_minutes: 7.2,
            utilization: 0.46,
            overloaded_slots: [],
            total_served: 48,
            end_backlog: 0
          },
          cashier: {
            avg_wait_minutes: 2.0,
            p95_wait_minutes: 4.0,
            utilization: 0.40,
            overloaded_slots: [],
            total_served: 70,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 2.8,
          p95_wait_minutes: 6.2,
          overloaded_slot_count: 0,
          total_served: 250,
          total_end_backlog: 0
        }
      },
      score: 91.5
    },
    optimized: {
      allocation: {
        label: "optimized",
        staff_by_queue: { teller: 4, loans: 2, customer_service: 2, cashier: 2 }
      },
      result: {
        allocation_label: "optimized",
        per_queue: {
          teller: {
            avg_wait_minutes: 3.1,
            p95_wait_minutes: 6.8,
            utilization: 0.52,
            overloaded_slots: [],
            total_served: 112,
            end_backlog: 0
          },
          loans: {
            avg_wait_minutes: 2.1,
            p95_wait_minutes: 4.5,
            utilization: 0.28,
            overloaded_slots: [],
            total_served: 20,
            end_backlog: 0
          },
          customer_service: {
            avg_wait_minutes: 3.4,
            p95_wait_minutes: 7.2,
            utilization: 0.46,
            overloaded_slots: [],
            total_served: 48,
            end_backlog: 0
          },
          cashier: {
            avg_wait_minutes: 2.0,
            p95_wait_minutes: 4.0,
            utilization: 0.40,
            overloaded_slots: [],
            total_served: 70,
            end_backlog: 0
          }
        },
        branch_wide: {
          avg_wait_minutes: 2.8,
          p95_wait_minutes: 6.2,
          overloaded_slot_count: 0,
          total_served: 250,
          total_end_backlog: 0
        }
      },
      score: 91.5
    },
    score_breakdown: {
      wait_score: 38.0,
      overload_score: 40.0,
      utilization_score: 13.5,
      reallocation_cost: 0.0,
      total_score: 91.5
    },
    improvement: {
      avg_wait_reduction_minutes: 0.0,
      p95_wait_reduction_minutes: 0.0,
      overloaded_slots_resolved: 0,
      utilization_delta: 0.0
    },
    explanation: "The branch is operating well within nominal service thresholds across all service counters. The baseline allocation (4-2-2-2) is already mathematically optimal with zero overloaded slots.",
    feasible: true
  }
};
