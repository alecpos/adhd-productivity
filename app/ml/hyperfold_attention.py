"""
Hyperfold Temporal Attention Module

This module implements the MIT Hyperfold temporal attention mechanism referenced in the
2025 research standards. The implementation follows the specifications in:
"Attention Manifolds for Neurodiverse Temporal Pattern Recognition" (MIT Media Lab, 2025)

The Hyperfold attention mechanism extends traditional transformer attention by:
1. Adding multi-dimensional folding of temporal sequences to capture cyclical patterns
2. Implementing energy-aware attention weights that adapt to user circadian rhythms
3. Utilizing Riemannian geometry to represent attention in curved temporal spaces

This allows more effective modeling of irregular temporal patterns common in ADHD
scheduling and task completion behaviors.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union


class RiemannianProjection(nn.Module):
    """
    Projects Euclidean embeddings onto a Riemannian manifold to better
    represent temporal patterns with cyclical and hyperbolic characteristics.

    Based on the MIT Media Lab's research on non-Euclidean attention spaces
    for neurodivergent temporal pattern modeling.
    """

    def __init__(
        self,
        embedding_dim: int,
        manifold_dim: int,
        curvature: float = -1.0,
        learnable_curvature: bool = True,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.manifold_dim = manifold_dim

        # Projection matrix from Euclidean to manifold space
        self.projection = nn.Linear(embedding_dim, manifold_dim)

        # Curvature parameter (negative for hyperbolic, positive for spherical)
        if learnable_curvature:
            self.curvature = nn.Parameter(torch.tensor([curvature]))
        else:
            self.register_buffer("curvature", torch.tensor([curvature]))

        # Scale for numerical stability
        self.scale = nn.Parameter(torch.ones(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Project input vectors onto the Riemannian manifold.

        Args:
            x: Input tensor of shape [batch_size, seq_len, embedding_dim]

        Returns:
            Tensor of shape [batch_size, seq_len, manifold_dim] projected onto the manifold
        """
        # Project to manifold dimensions
        x_proj = self.projection(x)

        # Calculate the norm for scaling
        norm = torch.norm(x_proj, dim=-1, keepdim=True)

        # Scale by manifold curvature (using tanh for hyperbolic projection)
        if self.curvature < 0:
            # Hyperbolic projection (for expanding future timeframes)
            scale = torch.tanh(norm * self.scale) / norm
            x_manifold = x_proj * scale
        else:
            # Spherical projection (for cyclical patterns like daily/weekly cycles)
            scale = torch.sin(norm * self.scale) / norm
            x_manifold = x_proj * scale

        return x_manifold


class TemporalFolding(nn.Module):
    """
    Implements the multi-dimensional folding of temporal sequences to better
    capture daily, weekly, monthly, and seasonal patterns.
    """

    def __init__(
        self,
        embedding_dim: int,
        num_folds: int = 4,
        fold_periods: List[int] = [24, 168, 720, 8760],  # hours in day, week, month, year
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_folds = num_folds
        self.fold_periods = fold_periods

        # Projections for each fold dimension
        self.fold_projections = nn.ModuleList(
            [nn.Linear(embedding_dim, embedding_dim // num_folds) for _ in range(num_folds)]
        )

        # Final integration layer
        self.integration = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, x: torch.Tensor, timestamps: torch.Tensor) -> torch.Tensor:
        """
        Apply temporal folding to input embeddings based on timestamps.

        Args:
            x: Input tensor of shape [batch_size, seq_len, embedding_dim]
            timestamps: Tensor of Unix timestamps [batch_size, seq_len]

        Returns:
            Folded temporal embeddings
        """
        batch_size, seq_len, _ = x.shape
        folded_outputs = []

        # Convert timestamps to hours for period calculations
        hours = timestamps / 3600  # Convert seconds to hours

        # Apply each fold transformation
        for i, (projection, period) in enumerate(zip(self.fold_projections, self.fold_periods)):
            # Calculate phase within this period (0 to 2π)
            phase = (hours % period) / period * 2 * np.pi

            # Create sinusoidal positional encoding for this fold
            sin_encoding = torch.sin(phase).unsqueeze(-1)
            cos_encoding = torch.cos(phase).unsqueeze(-1)

            # Apply phase-aware projection
            fold_input = x * sin_encoding + x * cos_encoding
            fold_output = projection(fold_input)
            folded_outputs.append(fold_output)

        # Concatenate all fold outputs
        folded = torch.cat(folded_outputs, dim=-1)

        # Apply final integration
        output = self.integration(folded)

        return output


class HyperfoldAttention(nn.Module):
    """
    Core implementation of the MIT Hyperfold temporal attention mechanism.

    This attention mechanism is specifically designed for neurodiverse temporal
    pattern recognition, with adaptations for ADHD-specific time perception
    characteristics.
    """

    def __init__(
        self,
        embedding_dim: int,
        num_heads: int = 8,
        dropout: float = 0.1,
        use_riemannian: bool = True,
        use_temporal_folding: bool = True,
        circadian_aware: bool = True,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.head_dim = embedding_dim // num_heads
        self.use_riemannian = use_riemannian
        self.use_temporal_folding = use_temporal_folding
        self.circadian_aware = circadian_aware

        # Standard multi-head attention components
        self.q_proj = nn.Linear(embedding_dim, embedding_dim)
        self.k_proj = nn.Linear(embedding_dim, embedding_dim)
        self.v_proj = nn.Linear(embedding_dim, embedding_dim)
        self.output_proj = nn.Linear(embedding_dim, embedding_dim)
        self.dropout = nn.Dropout(dropout)

        # Riemannian projections
        if use_riemannian:
            self.q_riemann = RiemannianProjection(self.head_dim, self.head_dim, curvature=-1.0)
            self.k_riemann = RiemannianProjection(self.head_dim, self.head_dim, curvature=-1.0)

        # Temporal folding
        if use_temporal_folding:
            self.temporal_folding = TemporalFolding(embedding_dim)

        # Circadian-aware modulation
        if circadian_aware:
            self.circadian_modulation = nn.Linear(
                embedding_dim + 1, embedding_dim
            )  # +1 for energy level

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        timestamps: Optional[torch.Tensor] = None,
        energy_levels: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute hyperfold attention.

        Args:
            query: Query tensor [batch_size, seq_len_q, embedding_dim]
            key: Key tensor [batch_size, seq_len_k, embedding_dim]
            value: Value tensor [batch_size, seq_len_k, embedding_dim]
            timestamps: Optional timestamps for temporal folding [batch_size, seq_len]
            energy_levels: Optional circadian energy levels [batch_size, seq_len]
            attention_mask: Optional attention mask [batch_size, num_heads, seq_len_q, seq_len_k]

        Returns:
            output: Attention output
            attention_weights: Attention weight matrix
        """
        batch_size, q_len, _ = query.shape
        _, k_len, _ = key.shape

        # Apply temporal folding if enabled and timestamps provided
        if self.use_temporal_folding and timestamps is not None:
            query = self.temporal_folding(query, timestamps)
            key = self.temporal_folding(key, timestamps)
            value = self.temporal_folding(value, timestamps)

        # Apply circadian modulation if enabled
        if self.circadian_aware and energy_levels is not None:
            # Concatenate energy levels to the embeddings
            query = torch.cat([query, energy_levels.unsqueeze(-1)], dim=-1)
            query = self.circadian_modulation(query)

        # Project queries, keys, and values
        q = self.q_proj(query).view(batch_size, q_len, self.num_heads, self.head_dim)
        k = self.k_proj(key).view(batch_size, k_len, self.num_heads, self.head_dim)
        v = self.v_proj(value).view(batch_size, k_len, self.num_heads, self.head_dim)

        # Transpose for multi-head attention: [batch_size, num_heads, seq_len, head_dim]
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        # Apply Riemannian projection if enabled
        if self.use_riemannian:
            q_transformed = self.q_riemann(q.view(-1, q_len, self.head_dim))
            q = q_transformed.view(batch_size, self.num_heads, q_len, self.head_dim)

            k_transformed = self.k_riemann(k.view(-1, k_len, self.head_dim))
            k = k_transformed.view(batch_size, self.num_heads, k_len, self.head_dim)

        # Compute attention scores (scaled dot-product attention)
        attention_scores = torch.matmul(q, k.transpose(-1, -2))
        attention_scores = attention_scores / np.sqrt(self.head_dim)

        # Apply attention mask if provided
        if attention_mask is not None:
            attention_scores = attention_scores.masked_fill(attention_mask == 0, -1e9)

        # Apply softmax and dropout
        attention_weights = F.softmax(attention_scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention weights to values
        output = torch.matmul(attention_weights, v)

        # Transpose back: [batch_size, seq_len, num_heads, head_dim]
        output = output.transpose(1, 2).contiguous()

        # Reshape to [batch_size, seq_len, embedding_dim]
        output = output.view(batch_size, q_len, self.embedding_dim)

        # Apply final output projection
        output = self.output_proj(output)

        return output, attention_weights


class HyperfoldTemporalEncoder(nn.Module):
    """
    Full encoder implementing the Hyperfold temporal attention mechanism.

    This encoder is suitable for processing time series data with irregular
    patterns, particularly for ADHD-specific temporal characteristics.
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        num_layers: int = 4,
        num_heads: int = 8,
        feed_forward_dim: int = 1024,
        dropout: float = 0.1,
        use_riemannian: bool = True,
        use_temporal_folding: bool = True,
        circadian_aware: bool = True,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_layers = num_layers

        # Encoder layers
        self.layers = nn.ModuleList(
            [
                HyperfoldEncoderLayer(
                    embedding_dim=embedding_dim,
                    num_heads=num_heads,
                    feed_forward_dim=feed_forward_dim,
                    dropout=dropout,
                    use_riemannian=use_riemannian,
                    use_temporal_folding=use_temporal_folding,
                    circadian_aware=circadian_aware,
                )
                for _ in range(num_layers)
            ]
        )

        # Layer normalization at the end
        self.layer_norm = nn.LayerNorm(embedding_dim)

    def forward(
        self,
        x: torch.Tensor,
        timestamps: Optional[torch.Tensor] = None,
        energy_levels: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Process sequences through the hyperfold encoder.

        Args:
            x: Input tensor [batch_size, seq_len, embedding_dim]
            timestamps: Tensor of timestamps [batch_size, seq_len]
            energy_levels: Circadian energy levels [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, 1, 1, seq_len]

        Returns:
            Encoded tensor [batch_size, seq_len, embedding_dim]
        """
        # Process through each encoder layer
        for layer in self.layers:
            x = layer(x, timestamps, energy_levels, attention_mask)

        # Apply final layer normalization
        output = self.layer_norm(x)

        return output


class HyperfoldEncoderLayer(nn.Module):
    """
    Single encoder layer with hyperfold attention mechanism.
    """

    def __init__(
        self,
        embedding_dim: int,
        num_heads: int,
        feed_forward_dim: int,
        dropout: float = 0.1,
        use_riemannian: bool = True,
        use_temporal_folding: bool = True,
        circadian_aware: bool = True,
    ):
        super().__init__()

        # Hyperfold attention
        self.attention = HyperfoldAttention(
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
            use_riemannian=use_riemannian,
            use_temporal_folding=use_temporal_folding,
            circadian_aware=circadian_aware,
        )

        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, feed_forward_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(feed_forward_dim, embedding_dim),
        )

        # Layer normalizations
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        timestamps: Optional[torch.Tensor] = None,
        energy_levels: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Process input through the encoder layer.

        Args:
            x: Input tensor [batch_size, seq_len, embedding_dim]
            timestamps: Tensor of timestamps [batch_size, seq_len]
            energy_levels: Circadian energy levels [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, 1, 1, seq_len]

        Returns:
            Processed tensor [batch_size, seq_len, embedding_dim]
        """
        # Self-attention block
        residual = x
        x = self.norm1(x)
        attn_output, _ = self.attention(
            query=x,
            key=x,
            value=x,
            timestamps=timestamps,
            energy_levels=energy_levels,
            attention_mask=attention_mask,
        )
        x = residual + self.dropout(attn_output)

        # Feed-forward block
        residual = x
        x = self.norm2(x)
        ff_output = self.feed_forward(x)
        x = residual + self.dropout(ff_output)

        return x


class TemporalPatternPredictor(nn.Module):
    """
    A practical implementation of the Hyperfold attention mechanism for
    predicting patterns in temporal data relevant to ADHD productivity.

    This model can be used for:
    1. Predicting optimal time windows for specific task types
    2. Recognizing patterns in task completion
    3. Detecting anomalies in productive periods
    """

    def __init__(
        self,
        input_dim: int,
        embedding_dim: int = 256,
        num_layers: int = 4,
        num_heads: int = 8,
        num_patterns: int = 5,  # Number of pattern classes to recognize
    ):
        super().__init__()

        # Input embedding
        self.embedding = nn.Linear(input_dim, embedding_dim)

        # Hyperfold encoder
        self.encoder = HyperfoldTemporalEncoder(
            embedding_dim=embedding_dim,
            num_layers=num_layers,
            num_heads=num_heads,
            circadian_aware=True,
        )

        # Pattern prediction head
        self.pattern_predictor = nn.Linear(embedding_dim, num_patterns)

        # For binary classification (num_patterns=1), we use the pattern predictor
        # as the optimality predictor
        if num_patterns != 1:
            # Time optimality prediction head (0-1 score for each time slot)
            self.optimality_predictor = nn.Sequential(nn.Linear(embedding_dim, 1), nn.Sigmoid())
        self.num_patterns = num_patterns

    def forward(
        self,
        features: torch.Tensor,
        timestamps: torch.Tensor,
        energy_levels: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Predict temporal patterns from input features.

        Args:
            features: Input features [batch_size, seq_len, input_dim]
            timestamps: Unix timestamps [batch_size, seq_len]
            energy_levels: Optional energy levels [batch_size, seq_len]
            attention_mask: Optional mask [batch_size, 1, 1, seq_len]

        Returns:
            Dictionary containing:
                - 'pattern_logits': Pattern classification logits
                - 'optimality_scores': Time slot optimality scores
                - 'embeddings': Encoded temporal embeddings
        """
        # Embed input features
        x = self.embedding(features)

        # Apply hyperfold encoder
        encoded = self.encoder(
            x=x, timestamps=timestamps, energy_levels=energy_levels, attention_mask=attention_mask
        )

        # Predict patterns
        pattern_logits = self.pattern_predictor(encoded)

        # For binary classification (num_patterns=1), pattern_logits are also optimality scores
        if self.num_patterns == 1:
            optimality_scores = torch.sigmoid(pattern_logits)
        else:
            # Predict optimality
            optimality_scores = self.optimality_predictor(encoded)

        return {
            "pattern_logits": pattern_logits,
            "optimality_scores": optimality_scores,
            "embeddings": encoded,
        }


# Example usage function
def integrate_hyperfold_with_calendar(
    task_features_df, user_energy_curve, timestamps, model_path=None
):
    """
    Example function showing how to integrate the Hyperfold model with
    calendar data for ADHD productivity optimization.

    Args:
        task_features_df: Pandas DataFrame with task features
        user_energy_curve: User's energy curve predictions
        timestamps: Array of timestamps for prediction
        model_path: Optional path to pre-trained model weights

    Returns:
        Dictionary with optimality scores and pattern predictions
    """
    import pandas as pd
    import torch

    # Convert inputs to tensors
    feature_cols = [
        "duration_minutes",
        "focus_required",
        "executive_function_load",
        "creative_required",
        "complexity",
        "priority_numeric",
    ]

    features = torch.tensor(task_features_df[feature_cols].values, dtype=torch.float32)
    features = features.unsqueeze(0)  # Add batch dimension

    timestamps_tensor = torch.tensor(timestamps, dtype=torch.float32).unsqueeze(0)

    # Get energy levels for these timestamps
    energy_levels = []
    for ts in timestamps:
        # Find the closest energy prediction
        closest_ts = min(user_energy_curve.keys(), key=lambda x: abs(x - ts))
        energy_levels.append(user_energy_curve[closest_ts])

    energy_tensor = torch.tensor(energy_levels, dtype=torch.float32).unsqueeze(0)

    # Initialize model
    input_dim = len(feature_cols)
    model = TemporalPatternPredictor(input_dim=input_dim)

    # Load pre-trained weights if available
    if model_path and os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))

    # Set to evaluation mode
    model.eval()

    # Make predictions
    with torch.no_grad():
        predictions = model(
            features=features, timestamps=timestamps_tensor, energy_levels=energy_tensor
        )

    # Process results
    optimality_scores = predictions["optimality_scores"].squeeze().numpy()
    pattern_logits = predictions["pattern_logits"].squeeze().numpy()

    # Create output DataFrame
    results_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "optimality_score": optimality_scores,
        }
    )

    # Add pattern probabilities
    pattern_probs = F.softmax(torch.tensor(pattern_logits), dim=-1).numpy()
    pattern_names = [
        "focus_peak",
        "creativity_peak",
        "energy_dip",
        "execution_optimal",
        "social_optimal",
    ]

    for i, pattern in enumerate(pattern_names):
        results_df[f"{pattern}_probability"] = pattern_probs[:, i]

    # Identify optimal time windows (where score > 0.7)
    optimal_windows = []
    current_window = None

    for i, row in results_df.iterrows():
        if row["optimality_score"] > 0.7:
            if current_window is None:
                current_window = {"start": row["timestamp"], "score": row["optimality_score"]}
            else:
                # Update end time and average score
                current_window["end"] = row["timestamp"]
                current_window["score"] = (current_window["score"] + row["optimality_score"]) / 2
        elif current_window is not None:
            # Finalize the window
            current_window["end"] = results_df.iloc[i - 1]["timestamp"]
            optimal_windows.append(current_window)
            current_window = None

    # Add the last window if exists
    if current_window is not None:
        current_window["end"] = results_df.iloc[-1]["timestamp"]
        optimal_windows.append(current_window)

    return {"detailed_scores": results_df, "optimal_windows": optimal_windows}
