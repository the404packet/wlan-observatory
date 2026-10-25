"""DCF Backoff stage management and Contention Window policies."""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BackoffStrategy(str, Enum):
    BEB = "BEB"  # Binary Exponential Backoff
    FIXED = "FIXED"  # Fixed Contention Window


@dataclass
class BackoffState:
    cw_min: int = 15
    cw_max: int = 1023
    retry_limit: int = 7
    strategy: BackoffStrategy = BackoffStrategy.BEB
    current_cw: Optional[int] = None
    stage: int = 0
    backoff_counter: int = 0
    consecutive_retries: int = 0

    def __post_init__(self):
        if self.current_cw is None:
            self.current_cw = self.cw_min

    def reset_cw(self, rng: random.Random) -> None:
        """Reset contention window following successful transmission."""
        self.stage = 0
        self.consecutive_retries = 0
        self.current_cw = self.cw_min
        self.backoff_counter = rng.randint(0, self.current_cw)

    def double_cw_on_failure(self, rng: random.Random) -> bool:
        """Exponentially double CW on collision or non-collision frame error.

        Returns True if packet is retained for retry, False if retry limit exceeded (drop).
        """
        self.consecutive_retries += 1
        if self.consecutive_retries > self.retry_limit:
            # Packet dropped due to retry limit exceeded
            self.reset_cw(rng)
            return False

        if self.strategy == BackoffStrategy.BEB:
            self.stage += 1
            # Standard 802.11 BEB: CW = min(2 * (CW + 1) - 1, cw_max)
            self.current_cw = min((self.current_cw + 1) * 2 - 1, self.cw_max)
        else:
            # Fixed strategy retains cw_min
            self.current_cw = self.cw_min

        self.backoff_counter = rng.randint(0, self.current_cw)
        return True

    def decrement(self) -> int:
        if self.backoff_counter > 0:
            self.backoff_counter -= 1
        return self.backoff_counter
