"""
Reinforcement learning policy for candidate triage.

Implements a threshold-based policy that can be upgraded to contextual bandits.
"""
import numpy as np
from typing import Literal, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyConfig:
    """Configuration for RL policy."""

    # Probability thresholds
    accept_threshold: float = 0.9
    reject_threshold: float = 0.3

    # False alarm rate target
    target_far: float = 0.01

    # Feature weights (for weighted scoring)
    weight_probability: float = 1.0
    weight_snr: float = 0.3
    weight_physics_checks: float = 0.2


class RLPolicy:
    """
    RL policy for candidate triage.

    Currently implements a calibrated threshold policy.
    Can be upgraded to Thompson sampling or contextual bandits.
    """

    def __init__(self, config: Optional[PolicyConfig] = None):
        """
        Initialize policy.

        Parameters
        ----------
        config : PolicyConfig, optional
            Policy configuration
        """
        self.config = config or PolicyConfig()
        self.action_counts = {"accept": 0, "reject": 0, "human_review": 0}
        self.reward_history = []

    def predict_action(
        self, probability: float, snr: float, physics_flags: Dict[str, bool], features: Optional[np.ndarray] = None
    ) -> Literal["accept", "reject", "human_review"]:
        """
        Predict action for a candidate.

        Parameters
        ----------
        probability : float
            Classifier probability (0-1)
        snr : float
            Signal-to-noise ratio
        physics_flags : Dict[str, bool]
            Physics validation flags
        features : np.ndarray, optional
            Additional features for contextual policy

        Returns
        -------
        str
            Action: "accept", "reject", or "human_review"
        """
        # Compute composite score
        score = self._compute_score(probability, snr, physics_flags)

        # Decision logic
        if score >= self.config.accept_threshold:
            # High confidence - accept
            if self._passes_physics_checks(physics_flags):
                action = "accept"
            else:
                # Failed physics - send to human
                action = "human_review"

        elif score <= self.config.reject_threshold:
            # Low confidence - reject
            action = "reject"

        else:
            # Uncertain - send to human review
            action = "human_review"

        # Track action
        self.action_counts[action] += 1

        return action

    def _compute_score(
        self, probability: float, snr: float, physics_flags: Dict[str, bool]
    ) -> float:
        """
        Compute weighted score from features.

        Parameters
        ----------
        probability : float
            Classifier probability
        snr : float
            SNR
        physics_flags : Dict[str, bool]
            Physics flags

        Returns
        -------
        float
            Composite score (0-1)
        """
        # Weighted combination
        w_prob = self.config.weight_probability
        w_snr = self.config.weight_snr
        w_physics = self.config.weight_physics_checks

        # Normalize SNR to 0-1 (assume SNR in [5, 20])
        snr_norm = np.clip((snr - 5.0) / 15.0, 0.0, 1.0)

        # Physics checks score (fraction passing)
        physics_score = sum(physics_flags.values()) / len(physics_flags)

        # Weighted average
        total_weight = w_prob + w_snr + w_physics
        score = (w_prob * probability + w_snr * snr_norm + w_physics * physics_score) / total_weight

        return float(score)

    def _passes_physics_checks(self, physics_flags: Dict[str, bool]) -> bool:
        """
        Check if candidate passes critical physics tests.

        Parameters
        ----------
        physics_flags : Dict[str, bool]
            Physics validation flags

        Returns
        -------
        bool
            True if all critical checks pass
        """
        # All flags should be True for acceptance
        critical_checks = ["odd_even_ok", "secondary_low", "density_consistent"]

        for check in critical_checks:
            if check in physics_flags and not physics_flags[check]:
                return False

        return True

    def update_thresholds(self, false_alarm_rate: float) -> None:
        """
        Adapt thresholds based on observed false alarm rate.

        Parameters
        ----------
        false_alarm_rate : float
            Observed FAR from validation
        """
        target_far = self.config.target_far

        if false_alarm_rate > target_far:
            # Too many false alarms - raise acceptance threshold
            self.config.accept_threshold = min(0.99, self.config.accept_threshold + 0.05)
            logger.info(
                f"FAR too high ({false_alarm_rate:.3f}), raising threshold to {self.config.accept_threshold:.2f}"
            )

        elif false_alarm_rate < target_far * 0.5:
            # Very few false alarms - can lower threshold slightly
            self.config.accept_threshold = max(0.7, self.config.accept_threshold - 0.02)
            logger.info(
                f"FAR low ({false_alarm_rate:.3f}), lowering threshold to {self.config.accept_threshold:.2f}"
            )

    def get_stats(self) -> Dict:
        """
        Get policy statistics.

        Returns
        -------
        Dict
            Action counts and current thresholds
        """
        total = sum(self.action_counts.values())

        return {
            "action_counts": self.action_counts.copy(),
            "action_fractions": {
                k: v / total if total > 0 else 0.0 for k, v in self.action_counts.items()
            },
            "thresholds": {
                "accept": self.config.accept_threshold,
                "reject": self.config.reject_threshold,
            },
            "total_decisions": total,
        }

    def save(self, path: str) -> None:
        """
        Save policy configuration to file.

        Parameters
        ----------
        path : str
            Save path
        """
        data = {
            "config": {
                "accept_threshold": self.config.accept_threshold,
                "reject_threshold": self.config.reject_threshold,
                "target_far": self.config.target_far,
                "weight_probability": self.config.weight_probability,
                "weight_snr": self.config.weight_snr,
                "weight_physics_checks": self.config.weight_physics_checks,
            },
            "stats": self.get_stats(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved policy to {path}")

    @classmethod
    def load(cls, path: str) -> "RLPolicy":
        """
        Load policy from file.

        Parameters
        ----------
        path : str
            Load path

        Returns
        -------
        RLPolicy
            Loaded policy
        """
        with open(path, "r") as f:
            data = json.load(f)

        config = PolicyConfig(**data["config"])
        policy = cls(config)

        # Restore stats if present
        if "stats" in data and "action_counts" in data["stats"]:
            policy.action_counts = data["stats"]["action_counts"]

        logger.info(f"Loaded policy from {path}")

        return policy


# Global policy instance
_policy_instance: Optional[RLPolicy] = None


def get_policy(config_path: Optional[str] = None) -> RLPolicy:
    """
    Get or create global policy instance.

    Parameters
    ----------
    config_path : str, optional
        Path to saved policy config

    Returns
    -------
    RLPolicy
        Global policy instance
    """
    global _policy_instance

    if _policy_instance is None:
        if config_path and Path(config_path).exists():
            _policy_instance = RLPolicy.load(config_path)
        else:
            _policy_instance = RLPolicy()

    return _policy_instance
