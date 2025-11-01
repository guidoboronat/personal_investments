"""
Data pipeline for ETL operations.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from copilot.core.base import BaseDataSource, BaseIndicator
from copilot.data.preprocessor import DataPreprocessor
from copilot.features.feature_engineering import FeatureEngineer
from copilot.core.exceptions import ValidationError


class DataPipeline:
    """Pipeline for data extraction, transformation, and loading."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_source: Optional[BaseDataSource] = None
        self.preprocessor = DataPreprocessor(config.get('preprocessor', {}))
        self.feature_engineer = FeatureEngineer(config.get('feature_engineer', {}))
        self.indicators: List[BaseIndicator] = []

    def set_data_source(self, data_source: BaseDataSource):
        """
        Set the data source for the pipeline.

        Args:
            data_source: Data source instance
        """
        self.data_source = data_source

    def add_indicator(self, indicator: BaseIndicator):
        """
        Add a technical indicator to the pipeline.

        Args:
            indicator: Indicator instance
        """
        self.indicators.append(indicator)

    def run(
        self,
        symbol: str,
        start_time: str,
        end_time: str,
        add_features: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Run the complete data pipeline.

        Args:
            symbol: Trading symbol
            start_time: Start time
            end_time: End time
            add_features: Whether to add engineered features
            **kwargs: Additional parameters for data source

        Returns:
            Processed DataFrame with indicators and features

        Raises:
            ValidationError: If data source is not set
        """
        if self.data_source is None:
            raise ValidationError("Data source not set. Call set_data_source() first.")

        # 1. Fetch data
        df = self.data_source.fetch_data(symbol, start_time, end_time, **kwargs)

        # 2. Clean and preprocess
        df = self.preprocessor.clean_data(df)

        # 3. Add technical indicators
        for indicator in self.indicators:
            df = indicator.calculate(df)

        # 4. Add engineered features
        if add_features:
            df = self.feature_engineer.create_features(df)

        # 5. Remove rows with NaN values created by indicators
        df = df.dropna()

        return df

    def run_incremental(
        self,
        symbol: str,
        last_n_periods: int = 100,
        **kwargs
    ) -> pd.DataFrame:
        """
        Run pipeline on most recent data (for live trading).

        Args:
            symbol: Trading symbol
            last_n_periods: Number of recent periods to fetch
            **kwargs: Additional parameters

        Returns:
            Processed DataFrame
        """
        # This is a simplified version - in production, you'd calculate
        # start_time and end_time based on last_n_periods
        raise NotImplementedError("Incremental pipeline not yet implemented")

    def validate_output(self, df: pd.DataFrame) -> bool:
        """
        Validate pipeline output.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if df.empty:
            raise ValidationError("Pipeline output is empty")

        # Check for NaN values
        if df.isnull().any().any():
            raise ValidationError("Pipeline output contains NaN values")

        return True
