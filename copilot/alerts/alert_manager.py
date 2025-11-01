"""
Alert manager for handling and dispatching alerts.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from copilot.core.exceptions import AlertError


class AlertManager:
    """Manager for creating and dispatching alerts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerts: List[Dict[str, Any]] = []
        self.handlers: List[Callable] = []
        self.enabled = self.config.get('enabled', True)

    def add_handler(self, handler: Callable):
        """
        Add an alert handler function.

        Args:
            handler: Function that takes alert dict as parameter
        """
        self.handlers.append(handler)

    def remove_handler(self, handler: Callable):
        """
        Remove an alert handler.

        Args:
            handler: Handler function to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler)

    def create_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = 'info',
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new alert.

        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity ('info', 'warning', 'critical')
            data: Additional alert data

        Returns:
            Alert dictionary
        """
        alert = {
            'id': len(self.alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(),
            'data': data or {},
            'acknowledged': False,
        }

        self.alerts.append(alert)
        
        if self.enabled:
            self._dispatch_alert(alert)

        return alert

    def _dispatch_alert(self, alert: Dict[str, Any]):
        """
        Dispatch alert to all handlers.

        Args:
            alert: Alert dictionary
        """
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                raise AlertError(f"Handler failed: {str(e)}")

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.

        Args:
            severity: Filter by severity
            acknowledged: Filter by acknowledged status

        Returns:
            List of alert dictionaries
        """
        filtered_alerts = self.alerts

        if severity is not None:
            filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity]

        if acknowledged is not None:
            filtered_alerts = [a for a in filtered_alerts if a['acknowledged'] == acknowledged]

        return filtered_alerts

    def acknowledge_alert(self, alert_id: int):
        """
        Mark an alert as acknowledged.

        Args:
            alert_id: ID of alert to acknowledge
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                return

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []

    def get_summary(self) -> Dict[str, Any]:
        """
        Get alert summary statistics.

        Returns:
            Dictionary with alert statistics
        """
        total = len(self.alerts)
        by_severity = {}
        
        for alert in self.alerts:
            severity = alert['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1

        acknowledged = sum(1 for a in self.alerts if a['acknowledged'])
        unacknowledged = total - acknowledged

        return {
            'total_alerts': total,
            'by_severity': by_severity,
            'acknowledged': acknowledged,
            'unacknowledged': unacknowledged,
        }

    def enable(self):
        """Enable alert dispatching."""
        self.enabled = True

    def disable(self):
        """Disable alert dispatching."""
        self.enabled = False
