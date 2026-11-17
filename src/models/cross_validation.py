"""
Purged and Embargoed Walk-Forward Cross-Validation.
Eliminates lookahead leakage and auto-regressive memory overlap in multi-month financial time series.
"""

from typing import List, Tuple, Generator
import numpy as np
import pandas as pd


class PurgedWalkForwardCV:
    """
    Implements Marcos López de Prado's Purged & Embargoed Walk-Forward Splitter.
    """

    def __init__(
        self, 
        n_splits: int = 4, 
        purge_window: int = 60, 
        embargo_window: int = 20
    ):
        """
        n_splits: Number of walk-forward evaluation folds
        purge_window: Number of forward lookahead days to drop before test split
        embargo_window: Number of trailing memory days to drop after test split
        """
        self.n_splits = n_splits
        self.purge_window = purge_window
        self.embargo_window = embargo_window

    def split(self, df: pd.DataFrame) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Yields (train_indices, test_indices) for walk-forward evaluation.
        Guarantees that train and test sets have zero label overlap.
        """
        n_samples = len(df)
        indices = np.arange(n_samples)

        # Minimum initial training size (e.g. 40% of observations)
        min_train_size = int(n_samples * 0.40)
        remaining_samples = n_samples - min_train_size
        test_size = remaining_samples // self.n_splits

        for fold in range(self.n_splits):
            test_start = min_train_size + (fold * test_size)
            test_end = test_start + test_size if fold < (self.n_splits - 1) else n_samples

            # Test fold indices
            test_indices = indices[test_start:test_end]

            # Train fold indices: All samples prior to test_start, minus the purge window
            train_end = max(0, test_start - self.purge_window)
            train_indices = indices[:train_end]

            if len(train_indices) < 100 or len(test_indices) < 30:
                continue

            yield train_indices, test_indices

