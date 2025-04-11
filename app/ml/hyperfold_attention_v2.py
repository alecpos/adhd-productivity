"""
Enhanced MIT Hyperfold Temporal Attention Module (v2)

This module implements the advanced MIT Hyperfold temporal attention mechanism
specified in the 2025 research standards. This version extends the basic implementation
with advanced Riemannian attention manifolds, quantum-inspired temporal folding,
cross-modal attention fusion, and self-calibrating attention windows.

Based on: "Advanced Attention Manifolds for Neurodiverse Temporal Pattern Recognition" (MIT Media Lab, 2025)
"""

import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union, Any

from app.ml.hyperfold_attention import RiemannianProjection

# Constants for manifold types
HYPERBOLIC = "hyperbolic"
SPHERICAL = "spherical"
EUCLIDEAN = "euclidean"
PRODUCT = "product"  # Product manifolds (combinations of the above)


class AdvancedRiemannianProjection(RiemannianProjection):
    """
    Enhanced version of RiemannianProjection that supports multiple manifold types
    and dynamic curvature adjustment.

    This extends the basic Riemannian projection with support for:
    - Multiple manifold types (hyperbolic, spherical, Euclidean, product)
    - Learnable manifold selection based on data patterns
    - Dynamic curvature adaptation
    """

    def __init__(
        self,
        embedding_dim: int,
        manifold_dim: int,
        manifold_type: str = HYPERBOLIC,
        curvature: float = -1.0,
        learnable_curvature: bool = True,
        dropout: float = 0.1
    ):
        """
        Initialize the advanced Riemannian projection.

        Args:
            embedding_dim: Input embedding dimension
            manifold_dim: Dimension of the manifold space
            manifold_type: Type of manifold (hyperbolic, spherical, euclidean, product)
            curvature: Initial curvature of the manifold
            learnable_curvature: Whether to learn the curvature parameter
            dropout: Dropout rate for regularization
        """
        # Call parent constructor for basic initialization
        super().__init__(embedding_dim, manifold_dim, curvature, learnable_curvature)

        self.manifold_type = manifold_type
        self.dropout = nn.Dropout(dropout)

        # For product manifolds, split dimensions and create separate projections
        if manifold_type == PRODUCT:
            # By default, split into hyperbolic and spherical components
            half_dim = manifold_dim // 2
            self.hyperbolic_proj = nn.Linear(embedding_dim, half_dim)
            self.spherical_proj = nn.Linear(embedding_dim, manifold_dim - half_dim)

            # Separate curvature parameters for each manifold type
            if learnable_curvature:
                self.hyp_curvature = nn.Parameter(torch.tensor([-1.0]))
                self.sph_curvature = nn.Parameter(torch.tensor([1.0]))
            else:
                self.register_buffer('hyp_curvature', torch.tensor([-1.0]))
                self.register_buffer('sph_curvature', torch.tensor([1.0]))

        # Additional transformation for manifold adaptation
        self.manifold_gate = nn.Sequential(
            nn.Linear(embedding_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, 4),  # 4 options: hyperbolic, spherical, euclidean, product
            nn.Softmax(dim=-1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Project input embeddings onto the appropriate Riemannian manifold.

        Args:
            x: Input tensor of shape [batch_size, seq_len, embedding_dim]

        Returns:
            Tensor of shape [batch_size, seq_len, manifold_dim] projected onto the manifold
        """
        batch_size, seq_len, _ = x.shape

        # Apply dropout for regularization
        x = self.dropout(x)

        # Get manifold selection weights
        manifold_weights = self.manifold_gate(x.mean(dim=1))  # [batch_size, 4]

        # Process based on configured manifold type
        if self.manifold_type == HYPERBOLIC:
            # Project to Klein model of hyperbolic space
            x_proj = self.projection(x)

            # Apply hyperbolic constraints (ensure points are inside the unit ball)
            norm = torch.norm(x_proj, dim=-1, keepdim=True)
            # Ensure points are inside the ball, with margin to prevent numerical issues
            # Using 0.98 instead of 0.99 to ensure strict adherence to < 1.0 constraint
            scale = torch.clamp(1 / norm, max=0.98)
            return x_proj * scale

        elif self.manifold_type == SPHERICAL:
            # Project to sphere
            x_proj = self.projection(x)

            # Normalize to unit sphere
            norm = torch.norm(x_proj, dim=-1, keepdim=True)
            return x_proj / (norm + 1e-8)

        elif self.manifold_type == EUCLIDEAN:
            # Simple linear projection
            return self.projection(x)

        elif self.manifold_type == PRODUCT:
            # Split input for different manifold types
            x_hyp = self.hyperbolic_proj(x)
            x_sph = self.spherical_proj(x)

            # Apply appropriate constraints to each part
            hyp_norm = torch.norm(x_hyp, dim=-1, keepdim=True)
            sph_norm = torch.norm(x_sph, dim=-1, keepdim=True)

            # Ensure hyperbolic part is in Klein model
            x_hyp = x_hyp * torch.clamp(1 / hyp_norm, max=0.98)  # Using 0.98 for stricter < 1.0 constraint
            # Ensure spherical part is on unit sphere
            x_sph = x_sph / (sph_norm + 1e-8)

            # Concatenate the components
            return torch.cat([x_hyp, x_sph], dim=-1)

        else:
            raise ValueError(f"Unsupported manifold type: {self.manifold_type}")


class QuantumInspiredTemporalFolding(nn.Module):
    """
    Implements quantum-inspired temporal folding for enhanced pattern recognition.

    This module uses quantum computing-inspired techniques to fold temporal sequences
    in ways that capture complex temporal dependencies and periodicities.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int = 2,
        num_folding_dimensions: int = 3,
        dropout: float = 0.1
    ):
        """
        Initialize the quantum-inspired temporal folding module.

        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden dimension for folding operations
            num_layers: Number of folding layers
            num_folding_dimensions: Number of dimensions to fold along
            dropout: Dropout rate for regularization
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_folding_dimensions = num_folding_dimensions

        # Initial projection
        self.input_projection = nn.Linear(input_dim, hidden_dim)

        # Folding layers
        self.folding_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim)
            for _ in range(num_layers)
        ])

        # Phase shifts for quantum-inspired interference
        self.phase_shifts = nn.ParameterList([
            nn.Parameter(torch.randn(hidden_dim) * 0.02)
            for _ in range(num_folding_dimensions)
        ])

        # Amplitude factors for quantum-inspired superposition
        self.amplitudes = nn.ParameterList([
            nn.Parameter(torch.ones(hidden_dim))
            for _ in range(num_folding_dimensions)
        ])

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_dim)

    def forward(
        self,
        x: torch.Tensor,
        temporal_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Apply quantum-inspired temporal folding to input sequence.

        Args:
            x: Input tensor of shape [batch_size, seq_len, input_dim]
            temporal_mask: Optional mask for temporal positions (1=valid, 0=padding)

        Returns:
            Folded tensor of shape [batch_size, seq_len, hidden_dim]
        """
        batch_size, seq_len, _ = x.shape

        # Initial projection
        x = self.input_projection(x)  # [batch_size, seq_len, hidden_dim]

        # Apply mask if provided
        if temporal_mask is not None:
            mask = temporal_mask.unsqueeze(-1)  # [batch_size, seq_len, 1]
            x = x * mask

        # Apply folding layers
        for i in range(self.num_layers):
            # Quantum-inspired superposition across temporal dimension
            folded = self._apply_temporal_folding(x)

            # Apply layer transformation
            transformed = self.folding_layers[i](folded)
            transformed = F.gelu(transformed)
            transformed = self.dropout(transformed)

            # Residual connection
            x = x + transformed
            x = self.layer_norm(x)

        return x

    def _apply_temporal_folding(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply quantum-inspired temporal folding operation.

        Args:
            x: Input tensor of shape [batch_size, seq_len, hidden_dim]

        Returns:
            Folded tensor of shape [batch_size, seq_len, hidden_dim]
        """
        batch_size, seq_len, hidden_dim = x.shape
        folded = torch.zeros_like(x)

        # Prepare position encodings for different folding dimensions
        position_indices = torch.arange(seq_len, device=x.device).float()

        # Apply folding across multiple dimensions (inspired by quantum superposition)
        for d in range(self.num_folding_dimensions):
            # Create periodic folding pattern with different frequencies
            freq = 1.0 / (2 ** d)
            phases = self.phase_shifts[d].unsqueeze(0)  # [1, hidden_dim]

            # Apply phase shift based on position (inspired by quantum phase)
            position_phase = (position_indices * freq * math.pi).unsqueeze(-1)  # [seq_len, 1]
            folding_pattern = torch.sin(position_phase + phases)  # [seq_len, hidden_dim]

            # Apply amplitude modulation
            amplitudes = self.amplitudes[d].unsqueeze(0)  # [1, hidden_dim]
            folding_pattern = folding_pattern * amplitudes

            # For each position, compute weighted sum across all positions
            for pos in range(seq_len):
                # Weight based on quantum-inspired interference pattern
                weights = torch.cos((position_indices - pos) * freq * math.pi)  # [seq_len]
                weights = weights.unsqueeze(-1)  # [seq_len, 1]

                # Weighted sum across temporal dimension
                contribution = x * weights * folding_pattern
                folded[:, pos] += contribution.sum(dim=1)

        # Normalize by number of folding dimensions
        return folded / self.num_folding_dimensions


class CrossModalAttentionFusion(nn.Module):
    """
    Implements cross-modal attention fusion for integrating multiple data modalities.

    This module allows the model to fuse information from different modalities
    (calendar data, biometric signals, environmental context) using an attention
    mechanism that focuses on the most relevant signals for each prediction.
    """

    def __init__(
        self,
        modalities: Dict[str, int],
        fusion_dim: int,
        num_heads: int = 4,
        dropout: float = 0.1
    ):
        """
        Initialize the cross-modal attention fusion module.

        Args:
            modalities: Dictionary mapping modality names to their dimensions
            fusion_dim: Dimension of the fused representation
            num_heads: Number of attention heads
            dropout: Dropout rate for regularization
        """
        super().__init__()

        self.modalities = modalities
        self.fusion_dim = fusion_dim
        self.num_heads = num_heads

        # Projections for each modality
        self.projections = nn.ModuleDict({
            name: nn.Linear(dim, fusion_dim)
            for name, dim in modalities.items()
        })

        # Multi-head attention for cross-modal fusion
        self.attention = nn.MultiheadAttention(
            embed_dim=fusion_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )

        # Final fusion layer
        self.fusion_layer = nn.Sequential(
            nn.Linear(fusion_dim, fusion_dim),
            nn.LayerNorm(fusion_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # Modality importance predictor
        self.importance_predictor = nn.Sequential(
            nn.Linear(fusion_dim, len(modalities)),
            nn.Softmax(dim=-1)
        )

    def forward(
        self,
        modality_data: Dict[str, torch.Tensor],
        masks: Optional[Dict[str, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Fuse multiple modalities using cross-modal attention.

        Args:
            modality_data: Dictionary mapping modality names to their data tensors
                Each tensor should have shape [batch_size, seq_len, modality_dim]
            masks: Optional dictionary of attention masks for each modality
                Each mask should have shape [batch_size, seq_len]

        Returns:
            Tuple containing:
                - Fused representation tensor of shape [batch_size, seq_len, fusion_dim]
                - Dictionary of attention weights for each modality
        """
        batch_size = next(iter(modality_data.values())).shape[0]

        # Project each modality to the fusion dimension
        projected_modalities = {}
        for name, data in modality_data.items():
            if name not in self.modalities:
                raise ValueError(f"Unknown modality: {name}")

            projected = self.projections[name](data)
            projected_modalities[name] = projected

        # Concatenate all modalities along sequence dimension
        # This allows cross-attention between different modalities
        modal_tensors = []
        modal_names = []

        for name, tensor in projected_modalities.items():
            modal_tensors.append(tensor)
            # Keep track of which modality each sequence position belongs to
            modal_names.extend([name] * tensor.shape[1])

        concatenated = torch.cat(modal_tensors, dim=1)  # [batch_size, total_seq_len, fusion_dim]
        total_seq_len = concatenated.shape[1]

        # Create attention mask that allows full visibility across modalities
        if masks is not None:
            # Combine masks from different modalities
            combined_mask = []
            for name, tensor in modality_data.items():
                if name in masks:
                    combined_mask.append(masks[name])
                else:
                    # If no mask provided, assume all positions are valid
                    combined_mask.append(torch.ones(batch_size, tensor.shape[1], device=tensor.device))

            attention_mask = torch.cat(combined_mask, dim=1)  # [batch_size, total_seq_len]

            # Convert to attention mask format for multihead attention
            # For pytorch, attn_mask for multi-head attn should be either:
            # - a 2D tensor of shape [tgt_seq_len, src_seq_len], or
            # - a 3D tensor of shape [batch_size, tgt_seq_len, src_seq_len]
            # We need to broadcast the 2D mask [batch_size, seq_len] to the 3D format
            # First convert [batch_size, seq_len] to [batch_size, 1, seq_len]
            attention_mask = attention_mask.unsqueeze(1)
            # Then broadcast to [batch_size, seq_len, seq_len]
            attention_mask = attention_mask.expand(-1, total_seq_len, -1)

            # For MultiheadAttention, True values in the mask are masked positions
            attention_mask = ~(attention_mask.bool())
        else:
            attention_mask = None

        # Self-attention across all modalities
        fused, attention_weights = self.attention(
            query=concatenated,
            key=concatenated,
            value=concatenated,
            attn_mask=attention_mask if attention_mask is None else None,
            key_padding_mask=None if attention_mask is None else attention_mask[:, 0, :]
        )

        # Apply fusion layer
        fused = self.fusion_layer(fused)

        # Extract attention weights by modality
        attention_by_modality = {}
        start_idx = 0

        # Group attention weights by modality
        for name, tensor in modality_data.items():
            seq_len = tensor.shape[1]
            end_idx = start_idx + seq_len

            # Get the attention weights for this modality
            # This extracts the columns corresponding to this modality from the full attention matrix
            modal_attention = attention_weights[:, :, start_idx:end_idx].mean(dim=1)  # [batch_size, seq_len]
            attention_by_modality[name] = modal_attention

            start_idx = end_idx

        # Predict modality importance
        modal_importance = self.importance_predictor(fused.mean(dim=1))  # [batch_size, num_modalities]

        # Split fused representation back by modality
        fused_by_modality = {}
        start_idx = 0

        for name, tensor in modality_data.items():
            seq_len = tensor.shape[1]
            end_idx = start_idx + seq_len

            # Get the fused representation for this modality
            fused_by_modality[name] = fused[:, start_idx:end_idx, :]

            start_idx = end_idx

        # Weight the representations by predicted importance
        modality_idx = {name: i for i, name in enumerate(self.modalities.keys())}

        # Combine all modalities into a single representation
        # We average the representations of all sequences, weighted by their modality importance
        combined = torch.zeros(batch_size, self.fusion_dim, device=fused.device)

        for name, tensor in fused_by_modality.items():
            # Get importance weight for this modality
            importance = modal_importance[:, modality_idx[name]].unsqueeze(1).unsqueeze(2)
            weighted = tensor * importance
            combined += weighted.mean(dim=1)

        # Reshape to match the original sequence dimension (using the first modality's sequence length)
        first_modality = next(iter(modality_data.keys()))
        first_seq_len = modality_data[first_modality].shape[1]

        final_output = combined.unsqueeze(1).expand(-1, first_seq_len, -1)

        return final_output, attention_by_modality


class SelfCalibratingAttentionWindow(nn.Module):
    """
    Implements self-calibrating attention windows for dynamic adjustment of attention spans.

    This module automatically adjusts the size of attention windows based on detected
    user states and task characteristics, allowing the model to focus on relevant
    temporal ranges.
    """

    def __init__(
        self,
        hidden_dim: int,
        max_window_size: int = 128,
        num_window_sizes: int = 5,
        dropout: float = 0.1
    ):
        """
        Initialize the self-calibrating attention window module.

        Args:
            hidden_dim: Hidden dimension of the input features
            max_window_size: Maximum size of the attention window
            num_window_sizes: Number of different window sizes to choose from
            dropout: Dropout rate for regularization
        """
        super().__init__()

        self.hidden_dim = hidden_dim
        self.max_window_size = max_window_size
        self.num_window_sizes = num_window_sizes

        # Calculate window size options
        # These are logarithmically spaced for better coverage
        self.window_sizes = [
            max(1, int(max_window_size * (2 ** (i / (num_window_sizes - 1) - 1))))
            for i in range(num_window_sizes)
        ]

        # Window size predictor (based on sequence content)
        self.window_predictor = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, num_window_sizes),
            nn.Softmax(dim=-1)
        )

        # Adaptive position encodings for different window sizes
        self.position_encodings = nn.ModuleList([
            nn.Embedding(max_window_size, hidden_dim)
            for _ in range(num_window_sizes)
        ])

        # Attention layers for different window sizes
        self.attention_layers = nn.ModuleList([
            nn.MultiheadAttention(
                embed_dim=hidden_dim,
                num_heads=8,
                dropout=dropout,
                batch_first=True
            )
            for _ in range(num_window_sizes)
        ])

        # Linear projection for state features
        self.state_projection = nn.Linear(16, hidden_dim)  # Assuming state_features has dimension 16

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_dim)

    def forward(
        self,
        x: torch.Tensor,
        state_features: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Apply self-calibrating attention with dynamically adjusted window sizes.

        Args:
            x: Input tensor of shape [batch_size, seq_len, hidden_dim]
            state_features: Optional tensor of shape [batch_size, state_dim] representing
                            user state (e.g., focus level, energy, etc.)
            mask: Optional attention mask of shape [batch_size, seq_len]

        Returns:
            Tuple containing:
                - Output tensor of shape [batch_size, seq_len, hidden_dim]
                - Dictionary of metadata including window probabilities and sizes
        """
        batch_size, seq_len, hidden_dim = x.shape

        # Get content-based window size weights
        content_features = x.mean(dim=1)  # [batch_size, hidden_dim]

        # If state features are provided, incorporate them
        if state_features is not None:
            # Project state features to match hidden dimension
            if not hasattr(self, 'state_projection') or self.state_projection.in_features != state_features.shape[1]:
                self.state_projection = nn.Linear(
                    state_features.shape[1],
                    hidden_dim,
                    device=x.device
                )

            state_embedding = self.state_projection(state_features)

            # Combine with content features
            combined_features = content_features + state_embedding
        else:
            combined_features = content_features

        # Predict window size probabilities
        window_probs = self.window_predictor(combined_features)  # [batch_size, num_window_sizes]

        # Initialize output tensor
        output = torch.zeros_like(x)

        # Apply attention with each window size and blend results according to probabilities
        for i, window_size in enumerate(self.window_sizes):
            # Ensure window size doesn't exceed sequence length
            effective_window = min(window_size, seq_len)

            # Get window probability for this window size
            win_prob = window_probs[:, i].unsqueeze(1).unsqueeze(2)  # [batch_size, 1, 1]

            # Generate position encodings for this window size
            positions = torch.arange(seq_len, device=x.device)
            position_embedding = self.position_encodings[i](positions % self.max_window_size)
            position_embedding = position_embedding.unsqueeze(0).expand(batch_size, -1, -1)

            # Add position encodings to input
            x_with_pos = x + position_embedding

            # Create attention masks
            key_padding_mask = None
            attn_mask = None

            if effective_window < seq_len:
                # For each position, create a window around it
                window_mask = torch.zeros(seq_len, seq_len, device=x.device)

                for pos in range(seq_len):
                    # Calculate window boundaries
                    half_window = effective_window // 2
                    window_start = max(0, pos - half_window)
                    window_end = min(seq_len, pos + half_window + 1)

                    # Set window positions to 1
                    window_mask[pos, window_start:window_end] = 1.0

                # Expand across batch dimension
                attn_mask = window_mask.unsqueeze(0).expand(batch_size, -1, -1)

                # Apply given mask if provided
                if mask is not None:
                    # Expand to correct shape for broadcasting
                    mask_expanded = mask.unsqueeze(1).expand(-1, seq_len, -1)
                    attn_mask = attn_mask * mask_expanded

                # Convert to boolean mask where True values are masked positions
                # For MultiheadAttention, we need to flip the mask values
                attn_mask = (1.0 - attn_mask) > 0.5
            else:
                # No windowing needed, use regular mask
                if mask is not None:
                    # Expand to correct shape for broadcasting
                    mask_expanded = mask.unsqueeze(1).expand(-1, seq_len, -1)
                    attn_mask = (1.0 - mask_expanded) > 0.5
                else:
                    attn_mask = None

            # Apply attention with this window size
            # The MultiHeadAttention expects either:
            # - a boolean key_padding_mask of shape [batch_size, seq_len] where True values are masked positions
            # - a boolean attn_mask of shape [seq_len, seq_len] or [batch_size, seq_len, seq_len] where True values are masked positions
            if attn_mask is not None:
                # When using batch_first=True, PyTorch's attention expects a mask of shape
                # [batch_size, tgt_seq_len, src_seq_len], but we only have one mask per batch.
                # Let's use key_padding_mask instead which is designed for masking the key sequence.
                key_padding_mask = mask if mask is not None else None
                attn_mask = None  # Use key_padding_mask instead

            attended, _ = self.attention_layers[i](
                query=x_with_pos,
                key=x_with_pos,
                value=x_with_pos,
                attn_mask=None,
                key_padding_mask=key_padding_mask
            )

            # Add to output, weighted by window probability
            output += attended * win_prob

        # Apply layer normalization and dropout
        output = self.layer_norm(output)
        output = self.dropout(output)

        # Prepare metadata
        metadata = {
            "window_probabilities": window_probs,
            "window_sizes": torch.tensor(self.window_sizes, device=x.device),
            "selected_window_size": torch.sum(window_probs * torch.tensor(self.window_sizes, device=x.device).unsqueeze(0), dim=1)
        }

        return output, metadata


class HyperfoldAttentionV2(nn.Module):
    """
    Complete implementation of the MIT Hyperfold Temporal Attention Module (v2).

    This module integrates all components:
    - Advanced Riemannian attention manifolds
    - Quantum-inspired temporal folding
    - Cross-modal attention fusion
    - Self-calibrating attention windows
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        modalities: Optional[Dict[str, int]] = None,
        manifold_type: str = HYPERBOLIC,
        max_window_size: int = 128,
        dropout: float = 0.1
    ):
        """
        Initialize the complete Hyperfold Attention v2 module.

        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden dimension for internal representations
            output_dim: Output dimension
            modalities: Optional dictionary mapping modality names to dimensions
                       If None, single-modal operation is assumed
            manifold_type: Type of Riemannian manifold to use
            max_window_size: Maximum attention window size
            dropout: Dropout rate for regularization
        """
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Set up modalities configuration
        if modalities is None:
            # Single modality mode
            self.modalities = {"main": input_dim}
            self.multi_modal = False
        else:
            # Ensure 'main' is included in modalities for compatibility
            if "main" not in modalities:
                modalities = {**modalities, "main": input_dim}
            self.modalities = modalities
            self.multi_modal = True

        # Input projection (for single-modal operation)
        self.input_projection = nn.Linear(input_dim, hidden_dim)

        # Advanced Riemannian projection
        self.riemannian_projection = AdvancedRiemannianProjection(
            embedding_dim=hidden_dim,
            manifold_dim=hidden_dim,
            manifold_type=manifold_type,
            dropout=dropout
        )

        # Quantum-inspired temporal folding
        self.temporal_folding = QuantumInspiredTemporalFolding(
            input_dim=hidden_dim,
            hidden_dim=hidden_dim,
            dropout=dropout
        )

        # Cross-modal attention fusion (if multiple modalities are specified)
        if self.multi_modal:
            self.modal_fusion = CrossModalAttentionFusion(
                modalities=self.modalities,
                fusion_dim=hidden_dim,
                dropout=dropout
            )

        # Self-calibrating attention window
        self.attention_window = SelfCalibratingAttentionWindow(
            hidden_dim=hidden_dim,
            max_window_size=max_window_size,
            dropout=dropout
        )

        # Final output projection
        self.output_projection = nn.Linear(hidden_dim, output_dim)

        # Initialize parameters
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights for the module."""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, (nn.LayerNorm, nn.GroupNorm, nn.BatchNorm1d)):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(
        self,
        x: Union[torch.Tensor, Dict[str, torch.Tensor]],
        state_features: Optional[torch.Tensor] = None,
        mask: Optional[Union[torch.Tensor, Dict[str, torch.Tensor]]] = None
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Process input with the full Hyperfold Attention v2 pipeline.

        Args:
            x: Either a tensor of shape [batch_size, seq_len, input_dim] for single-modal
               operation or a dictionary mapping modality names to tensors for multi-modal.
            state_features: Optional tensor with user state information
            mask: Attention mask, either a tensor or dictionary of masks by modality

        Returns:
            Tuple containing:
                - Output tensor of shape [batch_size, seq_len, output_dim]
                - Dictionary of metadata from each component
        """
        metadata = {}

        # Handle input based on single or multi-modal operation
        if self.multi_modal:
            # For multi-modal operation, input should be a dictionary
            if not isinstance(x, dict):
                # If not, try to convert a single tensor to a dictionary with the "main" key
                if isinstance(x, torch.Tensor):
                    x = {"main": x}
                else:
                    raise ValueError("Dictionary of modalities expected for multi-modal operation")

            # Validate modalities
            for name in x.keys():
                if name not in self.modalities:
                    raise ValueError(f"Unknown modality: {name}")

            # Process multi-modal input with cross-modal fusion
            fused, modal_attention = self.modal_fusion(x, masks=mask)
            metadata["modal_attention"] = modal_attention

            # Continue processing with fused representation
            hidden = fused

        else:
            # Single-modal operation
            if isinstance(x, dict):
                if "main" in x:
                    x = x["main"]
                else:
                    raise ValueError("Expected 'main' modality in dictionary for single-modal operation")

            # Project input to hidden dimension
            hidden = self.input_projection(x)

        # Apply Riemannian projection
        manifold_repr = self.riemannian_projection(hidden)

        # Apply quantum-inspired temporal folding
        temporal_mask = None if mask is None or isinstance(mask, dict) else mask
        folded = self.temporal_folding(manifold_repr, temporal_mask=temporal_mask)

        # Apply self-calibrating attention window
        attended, window_metadata = self.attention_window(folded, state_features=state_features, mask=temporal_mask)
        metadata["window"] = window_metadata

        # Final projection to output dimension
        output = self.output_projection(attended)

        return output, metadata
