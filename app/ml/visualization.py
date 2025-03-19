import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE


class InsightVisualizer:
    """
    Visualization tools for analyzing relationships in user data.
    """

    def __init__(self):
        self.color_palette = sns.color_palette("husl", 8)
        plt.style.use("seaborn")

    def create_correlation_heatmap(
        self, data: pd.DataFrame, title: str = "Feature Correlations"
    ) -> go.Figure:
        """
        Create an interactive correlation heatmap.
        """
        corr_matrix = data.corr()

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale="RdBu",
                zmin=-1,
                zmax=1,
            )
        )

        fig.update_layout(title=title, xaxis_title="Features", yaxis_title="Features")

    def visualize_time_patterns(
        self, timestamps: List[datetime], values: List[float], metric_name: str
    ) -> go.Figure:
        """
        Create an interactive time series visualization.
        """
        df = pd.DataFrame({"timestamp": timestamps, "value": values})

        # Add time-based features
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                f"{metric_name} Over Time",
                f"Average {metric_name} by Hour",
            ),
        )

        # Time series plot
        fig.add_trace(
            go.Scatter(x=df["timestamp"], y=df["value"], mode="lines+markers", name=metric_name),
            row=1,
            col=1,
        )

        # Hourly patterns
        hourly_avg = df.groupby("hour")["value"].mean()
        fig.add_trace(
            go.Bar(x=hourly_avg.index, y=hourly_avg.values, name=f"Hourly {metric_name}"),
            row=2,
            col=1,
        )

        fig.update_layout(height=800, title_text=f"{metric_name} Analysis")

    def create_feature_importance_plot(
        self, feature_names: List[str], importance_scores: List[float]
    ) -> go.Figure:
        """
        Create an interactive feature importance visualization.
        """
        # Sort features by importance
        sorted_idx = np.argsort(importance_scores)
        pos = np.arange(sorted_idx.shape[0]) + 0.5

        fig = go.Figure(
            data=go.Bar(
                x=importance_scores[sorted_idx],
                y=[feature_names[i] for i in sorted_idx],
                orientation="h",
            )
        )

        fig.update_layout(
            title="Feature Importance Analysis",
            xaxis_title="Importance Score",
            yaxis_title="Features",
            height=max(400, len(feature_names) * 20),
        )

    def visualize_user_clusters(
        self,
        features: np.ndarray,
        labels: Optional[np.ndarray] = None,
        n_components: int = 2,
    ) -> go.Figure:
        """
        Create an interactive visualization of user clusters using t-SNE.
        """
        # Reduce dimensionality using t-SNE
        tsne = TSNE(n_components=n_components, random_state=42)
        reduced_features = tsne.fit_transform(features)

        if labels is None:
            labels = np.zeros(len(features))

        # Create scatter plot
        fig = go.Figure(
            data=go.Scatter(
                x=reduced_features[:, 0],
                y=reduced_features[:, 1],
                mode="markers",
                marker=dict(size=10, color=labels, colorscale="Viridis", showscale=True),
                text=[f"UserModelSchemaSchema {i}" for i in range(len(features))],
            )
        )

        fig.update_layout(
            title="UserModelSchemaSchema Clustering Visualization",
            xaxis_title="t-SNE Component 1",
            yaxis_title="t-SNE Component 2",
        )

    def create_productivity_dashboard(
        self, mood_data: List[Dict], energy_data: List[Dict], task_data: List[Dict]
    ) -> Dict[str, go.Figure]:
        """
        Create a comprehensive dashboard of productivity metrics.
        """
        dashboard = {}

        # Mood trends
        mood_times = [d["timestamp"] for d in mood_data]
        mood_values = [d["mood_score"] for d in mood_data]
        dashboard["mood_trends"] = self.visualize_time_patterns(
            mood_times, mood_values, "Mood Score"
        )

        # Energy patterns
        energy_times = [d["timestamp"] for d in energy_data]
        energy_values = [d["energy_level"] for d in energy_data]
        dashboard["energy_patterns"] = self.visualize_time_patterns(
            energy_times, energy_values, "Energy Level"
        )

        # TaskModelSchemaSchema completion analysis
        task_df = pd.DataFrame(task_data)
        dashboard["task_completion"] = self._create_task_completion_analysis(task_df)

        # Correlation analysis
        combined_df = self._combine_metrics(mood_data, energy_data, task_data)
        dashboard["correlations"] = self.create_correlation_heatmap(combined_df)

    def _create_task_completion_analysis(self, task_df: pd.DataFrame) -> go.Figure:
        """
        Create detailed task completion analysis visualization.
        """
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Completion Rate by Category",
                "TaskModelSchemaSchema Duration Distribution",
                "Completion Rate by Priority",
                "TaskModelSchemaSchema Complexity vs. Completion",
            ),
        )

        # Completion rate by category
        completion_by_category = task_df.groupby("category")["completed"].mean()
        fig.add_trace(
            go.Bar(
                x=completion_by_category.index,
                y=completion_by_category.values,
                name="Category Completion",
            ),
            row=1,
            col=1,
        )

        # TaskModelSchemaSchema duration distribution
        fig.add_trace(
            go.Histogram(x=task_df["time_spent"], name="Duration Distribution"),
            row=1,
            col=2,
        )

        # Completion rate by priority
        completion_by_priority = task_df.groupby("priority_level")["completed"].mean()
        fig.add_trace(
            go.Bar(
                x=completion_by_priority.index,
                y=completion_by_priority.values,
                name="Priority Completion",
            ),
            row=2,
            col=1,
        )

        # TaskModelSchemaSchema complexity vs. completion
        fig.add_trace(
            go.Scatter(
                x=task_df["difficulty_rating"],
                y=task_df["completed"],
                mode="markers",
                name="Complexity Impact",
            ),
            row=2,
            col=2,
        )

        fig.update_layout(height=800, title_text="TaskModelSchemaSchema Completion Analysis")

    def _combine_metrics(
        self, mood_data: List[Dict], energy_data: List[Dict], task_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Combine different metrics into a single DataFrame for correlation analysis.
        """
        # Create separate DataFrames
        mood_df = pd.DataFrame(mood_data)
        energy_df = pd.DataFrame(energy_data)
        task_df = pd.DataFrame(task_data)

        # Resample to common timepoints
        mood_df.set_index("timestamp", inplace=True)
        energy_df.set_index("timestamp", inplace=True)
        task_df.set_index("timestamp", inplace=True)

        # Combine metrics
        combined_df = pd.concat(
            [
                mood_df["mood_score"],
                energy_df["energy_level"],
                task_df["completed"].astype(float),
            ],
            axis=1,
        )

        combined_df.columns = ["mood_score", "energy_level", "task_completion"]
        return combined_df.fillna(method="ffill")
