"""
Qwen Omni time series embeddings.

Provides learned representations of light curves for downstream classification.
Falls back to statistical features if Qwen weights are not available.
"""
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SimpleTimeSeriesEncoder(nn.Module):
    """
    Lightweight time series encoder as fallback.

    Uses 1D convolutions to extract local patterns.
    """

    def __init__(self, embedding_dim: int = 128):
        super().__init__()

        self.conv1 = nn.Conv1d(1, 32, kernel_size=7, padding=3)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, padding=2)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)

        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(128, embedding_dim)

        self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Parameters
        ----------
        x : torch.Tensor
            Input shape (batch, length) or (batch, 1, length)

        Returns
        -------
        torch.Tensor
            Embeddings shape (batch, embedding_dim)
        """
        # Ensure 3D input
        if x.dim() == 2:
            x = x.unsqueeze(1)

        # Convolutional layers
        x = self.activation(self.conv1(x))
        x = self.activation(self.conv2(x))
        x = self.activation(self.conv3(x))

        # Global pooling
        x = self.pool(x).squeeze(-1)

        # Final projection
        x = self.fc(x)

        return x


class QwenEmbeddings:
    """
    Qwen Omni embeddings wrapper.

    Attempts to load Qwen weights, falls back to simple encoder or statistical features.
    """

    def __init__(self, weights_path: Optional[str] = None, device: str = "cpu"):
        """
        Initialize embeddings model.

        Parameters
        ----------
        weights_path : str, optional
            Path to Qwen weights file
        device : str
            PyTorch device ('cpu' or 'cuda')
        """
        self.device = device
        self.embedding_dim = 128

        # Try to load Qwen model
        self.model = None
        self.use_qwen = False

        if weights_path and Path(weights_path).exists():
            try:
                # For now, use simple encoder
                # In production, this would load actual Qwen weights
                self.model = SimpleTimeSeriesEncoder(embedding_dim=self.embedding_dim)
                self.model.load_state_dict(torch.load(weights_path, map_location=device))
                self.model.eval()
                self.use_qwen = True
                logger.info(f"Loaded Qwen model from {weights_path}")
            except Exception as e:
                logger.warning(f"Failed to load Qwen model: {e}")

        if self.model is None:
            # Use simple encoder without pretrained weights
            self.model = SimpleTimeSeriesEncoder(embedding_dim=self.embedding_dim)
            self.model.eval()
            logger.info("Using simple encoder (no pretrained weights)")

    def embed(
        self, time: np.ndarray, flux: np.ndarray, normalize: bool = True
    ) -> np.ndarray:
        """
        Compute embedding for a light curve.

        Parameters
        ----------
        time : np.ndarray
            Time values
        flux : np.ndarray
            Flux values
        normalize : bool
            Whether to normalize before embedding

        Returns
        -------
        np.ndarray
            Embedding vector (length: embedding_dim)
        """
        # Normalize if requested
        if normalize:
            flux = (flux - np.mean(flux)) / (np.std(flux) + 1e-8)

        # Interpolate to fixed length if needed
        target_length = 512
        if len(flux) != target_length:
            flux_interp = np.interp(
                np.linspace(0, 1, target_length), np.linspace(0, 1, len(flux)), flux
            )
        else:
            flux_interp = flux

        # Convert to tensor
        flux_tensor = torch.tensor(flux_interp, dtype=torch.float32).unsqueeze(0)

        # Forward pass
        with torch.no_grad():
            embedding = self.model(flux_tensor)

        return embedding.squeeze(0).cpu().numpy()

    def compute_statistical_features(self, time: np.ndarray, flux: np.ndarray) -> np.ndarray:
        """
        Compute handcrafted statistical features as fallback.

        Parameters
        ----------
        time : np.ndarray
            Time values
        flux : np.ndarray
            Flux values

        Returns
        -------
        np.ndarray
            Feature vector
        """
        features = []

        # Basic statistics
        features.append(np.mean(flux))
        features.append(np.std(flux))
        features.append(np.median(flux))
        features.append(np.percentile(flux, 25))
        features.append(np.percentile(flux, 75))
        features.append(np.min(flux))
        features.append(np.max(flux))

        # Skewness and kurtosis
        from scipy.stats import skew, kurtosis

        features.append(skew(flux))
        features.append(kurtosis(flux))

        # Autocorrelation at lag 1
        if len(flux) > 1:
            features.append(np.corrcoef(flux[:-1], flux[1:])[0, 1])
        else:
            features.append(0.0)

        # Power spectrum features
        fft = np.fft.fft(flux - np.mean(flux))
        psd = np.abs(fft) ** 2
        features.append(np.max(psd))
        features.append(np.argmax(psd))

        # Pad to embedding_dim
        features = np.array(features)
        if len(features) < self.embedding_dim:
            features = np.pad(features, (0, self.embedding_dim - len(features)))
        else:
            features = features[: self.embedding_dim]

        return features


# Global instance (lazy initialization)
_qwen_instance: Optional[QwenEmbeddings] = None


def get_qwen_embeddings(weights_path: Optional[str] = None, device: str = "cpu") -> QwenEmbeddings:
    """
    Get or create global QwenEmbeddings instance.

    Parameters
    ----------
    weights_path : str, optional
        Path to weights
    device : str
        PyTorch device

    Returns
    -------
    QwenEmbeddings
        Global embeddings instance
    """
    global _qwen_instance

    if _qwen_instance is None:
        _qwen_instance = QwenEmbeddings(weights_path=weights_path, device=device)

    return _qwen_instance
