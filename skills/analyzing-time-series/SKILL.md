---
name: analyzing-time-series
description: Comprehensive diagnostic analysis of time series data. Use when users provide CSV time series data and want to understand its characteristics before forecasting — including stationarity, seasonality, trend, forecastability, and transformation recommendations.
license: MIT
compatibility: Python (pandas, numpy, statsmodels, matplotlib, scipy)
allowed-tools: run_code run_command read_file write_to_file create_file list_directory make_directory

goal: >
  Perform deep diagnostic analysis of time series datasets to determine their statistical
  properties, forecastability, structural patterns, and necessary transformations prior
  to modeling and forecasting.

capabilities:
  - stationarity_testing
  - seasonality_detection
  - trend_analysis
  - forecastability_assessment
  - statistical_diagnostics
  - transform_recommendation
  - automated_plot_generation
  - data_quality_analysis

input_format:
  required_columns:
    - date: Timestamp or date column (e.g., date, timestamp, time)
    - value: Numeric measurement column (e.g., value, sales, temperature)
  file_type: CSV

workflow:
  step_1_run_diagnostics:
    command: python scripts/diagnose.py data.csv --output-dir results/
    outputs:
      - diagnostics.json
      - summary.txt
    notes:
      - Column names auto-detected
      - Can override using --date-col and --value-col

  step_2_generate_plots:
    command: python scripts/visualize.py data.csv --output-dir results/
    outputs:
      - plots/ directory
    notes:
      - Must run after diagnostics
      - Ensures synchronized ACF/PACF and stationarity outputs

  step_3_report_results:
    - Summarize findings from summary.txt
    - Present relevant plots
    - Interpret results using references/interpretation.md

script_options:
  - --date-col NAME: Specify date column
  - --value-col NAME: Specify value column
  - --output-dir PATH: Output directory (default: diagnostics/)
  - --seasonal-period N: Manual seasonal period override

outputs:
  structure: |
    results/
    ├── diagnostics.json
    ├── summary.txt
    ├── diagnostics_state.json
    └── plots/
        ├── timeseries.png
        ├── histogram.png
        ├── rolling_stats.png
        ├── box_by_dayofweek.png
        ├── box_by_month.png
        ├── box_by_quarter.png
        ├── acf_pacf.png
        ├── decomposition.png
        └── lag_scatter.png

analysis_dimensions:
  - stationarity:
      - ADF test
      - KPSS test
      - required differencing order
  - seasonality:
      - seasonal period detection
      - frequency-based seasonality inference
  - trend:
      - direction detection
      - strength estimation
  - distribution:
      - histogram analysis
      - skewness
      - kurtosis
  - autocorrelation:
      - ACF
      - PACF
      - lag dependency
  - variance_stability:
      - rolling statistics
      - heteroscedasticity detection
  - transform_need:
      - log transform
      - box-cox
      - differencing

best_practices:
  - Always run full diagnostics before modeling
  - Inspect both numeric metrics and plots
  - Validate stationarity before forecasting
  - Identify seasonality before selecting models
  - Apply recommended transformations prior to training

common_pitfalls:
  - Skipping diagnostics and directly forecasting
  - Ignoring seasonality detection
  - Not applying differencing when required
  - Misinterpreting autocorrelation plots

references:
  - references/interpretation.md: Statistical thresholds, seasonality heuristics, transform guidance

dependencies:
  - pandas
  - numpy
  - matplotlib
  - statsmodels
  - scipy
---