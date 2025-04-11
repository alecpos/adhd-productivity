#!/usr/bin/env python
"""
Visualization script for weekly task transition data analysis.

This script visualizes the output from weekly_resampling_demo.py,
creating charts to help understand transition time patterns.
"""

import json
import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def load_analysis_data(file_path="weekly_transition_analysis.json"):
    """Load the analysis data from JSON file."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found. Run weekly_resampling_demo.py first.")
        sys.exit(1)

    with open(file_path, "r") as f:
        data = json.load(f)

    return data


def create_weekly_trend_chart(data):
    """Create a chart showing weekly transition time trends."""
    # Extract weekly data
    weekly_data = data["weekly_transitions"]

    # Convert to DataFrame
    df = pd.DataFrame(weekly_data)

    # Convert timestamp to datetime if it's not already
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Set up the figure
    plt.figure(figsize=(12, 6))

    # Plot mean transition times
    if "actual_minutes_mean" in df.columns:
        plt.plot(df["timestamp"], df["actual_minutes_mean"], "o-", label="Actual Minutes (Mean)")

    if "predicted_minutes_mean" in df.columns:
        plt.plot(
            df["timestamp"], df["predicted_minutes_mean"], "s--", label="Predicted Minutes (Mean)"
        )

    # Add rolling average if available
    rolling_avg = []
    for col in df.columns:
        if "rolling" in col and "actual_minutes" in col:
            rolling_avg.append(col)

    for col in rolling_avg:
        if col in df.columns:
            plt.plot(df["timestamp"], df[col], "-", label=f"{col}")

    plt.title("Weekly Transition Time Trends")
    plt.xlabel("Week")
    plt.ylabel("Minutes")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    return plt.gcf()


def create_day_of_week_chart(data):
    """Create a chart showing transition time patterns by day of week."""
    # Extract day of week data
    day_patterns = data["patterns"]["day_of_week"]

    # We'll focus on actual minutes
    if "actual_minutes" not in day_patterns:
        print("Warning: No actual_minutes data found in day patterns")
        return None

    # Create a DataFrame from the day patterns
    days = list(day_patterns["actual_minutes"]["mean"].keys())
    means = [day_patterns["actual_minutes"]["mean"][day] for day in days]
    stds = [day_patterns["actual_minutes"]["std"][day] for day in days]

    # Sort days in correct order
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_indices = [day_order.index(day) for day in days]
    sorted_days = [days[i] for i in sorted(range(len(days)), key=lambda k: sorted_indices[k])]
    sorted_means = [means[i] for i in sorted(range(len(means)), key=lambda k: sorted_indices[k])]
    sorted_stds = [stds[i] for i in sorted(range(len(stds)), key=lambda k: sorted_indices[k])]

    # Set up the figure
    plt.figure(figsize=(10, 6))

    # Create bar chart with error bars
    x = np.arange(len(sorted_days))
    plt.bar(
        x, sorted_means, yerr=sorted_stds, align="center", alpha=0.7, ecolor="black", capsize=10
    )
    plt.xlabel("Day of Week")
    plt.ylabel("Transition Time (minutes)")
    plt.title("Average Transition Time by Day of Week")
    plt.xticks(x, sorted_days)
    plt.grid(True, alpha=0.3, axis="y")

    # Add numeric values on top of bars
    for i, v in enumerate(sorted_means):
        plt.text(i, v + 0.5, f"{v:.1f}", ha="center")

    plt.tight_layout()

    return plt.gcf()


def create_heatmap(data):
    """Create a heatmap showing transition time patterns."""
    weekly_data = data["weekly_transitions"]
    df = pd.DataFrame(weekly_data)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["week_number"] = df["timestamp"].dt.isocalendar().week
        df["week_year"] = df["timestamp"].dt.isocalendar().year

    # Get columns that represent metrics (means)
    metric_cols = [col for col in df.columns if col.endswith("_mean") and "wow_change" not in col]

    # Set up the figure
    plt.figure(figsize=(12, 8))

    # Create a pivot table for the heatmap
    if len(metric_cols) > 0 and "week_number" in df.columns:
        # Use a subset of metrics for readability
        core_metrics = [
            col
            for col in metric_cols
            if col
            in [
                "actual_minutes_mean",
                "predicted_minutes_mean",
                "prediction_error_mean",
                "context_score_mean",
            ]
        ]

        # Normalize data for better visualization
        normalized_df = df.copy()
        for col in core_metrics:
            if col in df.columns:
                # Min-max normalization
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    normalized_df[col] = (df[col] - min_val) / (max_val - min_val)

        # Create the heatmap
        pivot_df = normalized_df.pivot_table(
            values=core_metrics, index="week_number", columns="week_year", aggfunc="mean"
        )

        # Plot the heatmap
        sns.heatmap(pivot_df, annot=False, cmap="YlGnBu", linewidths=0.5, fmt=".2f")
        plt.title("Weekly Transition Metrics Heatmap (Normalized)")
        plt.tight_layout()
    else:
        plt.text(
            0.5,
            0.5,
            "Insufficient data for heatmap",
            horizontalalignment="center",
            verticalalignment="center",
        )

    return plt.gcf()


def create_histogram(data):
    """Create histograms of transition times."""
    weekly_data = data["weekly_transitions"]
    df = pd.DataFrame(weekly_data)

    # Set up the figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot actual minutes distribution
    if "actual_minutes_mean" in df.columns:
        sns.histplot(df["actual_minutes_mean"], kde=True, ax=axes[0])
        axes[0].set_title("Distribution of Actual Transition Times")
        axes[0].set_xlabel("Minutes")
        axes[0].set_ylabel("Frequency")
        axes[0].grid(True, alpha=0.3)

    # Plot prediction error distribution
    if "prediction_error_mean" in df.columns:
        sns.histplot(df["prediction_error_mean"], kde=True, ax=axes[1])
        axes[1].set_title("Distribution of Prediction Errors")
        axes[1].set_xlabel("Minutes (Actual - Predicted)")
        axes[1].set_ylabel("Frequency")
        axes[1].grid(True, alpha=0.3)

        # Add a vertical line at zero
        axes[1].axvline(x=0, color="r", linestyle="--", alpha=0.7)

    plt.tight_layout()

    return fig


def main():
    """Main function to generate all visualizations."""
    # Load the analysis data
    data = load_analysis_data()

    # Create output directory if it doesn't exist
    output_dir = "weekly_transition_analysis_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate and save visualizations
    charts = {
        "weekly_trend": create_weekly_trend_chart,
        "day_of_week": create_day_of_week_chart,
        "heatmap": create_heatmap,
        "histogram": create_histogram,
    }

    for name, chart_func in charts.items():
        try:
            fig = chart_func(data)
            if fig:
                output_path = os.path.join(output_dir, f"{name}.png")
                fig.savefig(output_path, dpi=300, bbox_inches="tight")
                print(f"Saved {output_path}")
                plt.close(fig)
        except Exception as e:
            print(f"Error creating {name} chart: {e}")

    print(f"Visualizations saved to {output_dir}/")


if __name__ == "__main__":
    main()
