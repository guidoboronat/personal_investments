"""
Rule engine for combining and evaluating multiple rules.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from copilot.core.base import BaseRule


class RuleEngine:
    """Engine for evaluating multiple trading rules."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules: List[BaseRule] = []
        self.logic = self.config.get('logic', 'AND')  # 'AND' or 'OR'

    def add_rule(self, rule: BaseRule):
        """
        Add a rule to the engine.

        Args:
            rule: Rule instance to add
        """
        self.rules.append(rule)

    def remove_rule(self, rule: BaseRule):
        """
        Remove a rule from the engine.

        Args:
            rule: Rule instance to remove
        """
        if rule in self.rules:
            self.rules.remove(rule)

    def clear_rules(self):
        """Clear all rules from the engine."""
        self.rules = []

    def evaluate(self, df: pd.DataFrame, row_idx: int) -> bool:
        """
        Evaluate all rules for a given data point.

        Args:
            df: DataFrame with market data
            row_idx: Current row index

        Returns:
            True if rules are satisfied based on logic
        """
        if not self.rules:
            return False

        results = [rule.evaluate(df, row_idx) for rule in self.rules]

        if self.logic == 'AND':
            return all(results)
        elif self.logic == 'OR':
            return any(results)
        else:
            return False

    def evaluate_all(self, df: pd.DataFrame) -> pd.Series:
        """
        Evaluate rules for all data points.

        Args:
            df: DataFrame with market data

        Returns:
            Series with evaluation results
        """
        results = []
        for idx in range(len(df)):
            results.append(self.evaluate(df, idx))
        return pd.Series(results, index=df.index)

    def get_rule_descriptions(self) -> List[str]:
        """
        Get descriptions of all rules.

        Returns:
            List of rule descriptions
        """
        return [rule.get_description() for rule in self.rules]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of the rule engine.

        Returns:
            Dictionary with engine summary
        """
        return {
            'num_rules': len(self.rules),
            'logic': self.logic,
            'rules': self.get_rule_descriptions(),
        }

    def set_logic(self, logic: str):
        """
        Set the logic operator.

        Args:
            logic: 'AND' or 'OR'
        """
        if logic not in ['AND', 'OR']:
            raise ValueError("Logic must be 'AND' or 'OR'")
        self.logic = logic
