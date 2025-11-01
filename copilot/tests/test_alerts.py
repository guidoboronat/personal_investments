"""
Tests for alerts module.
"""

import unittest
from copilot.alerts.alert_manager import AlertManager
from copilot.alerts.alert_types import PriceAlert, VolumeAlert


class TestAlertManager(unittest.TestCase):
    """Test alert manager."""

    def test_create_alert(self):
        """Test alert creation."""
        manager = AlertManager()
        
        alert = manager.create_alert(
            alert_type='price',
            message='Test alert',
            severity='info'
        )
        
        self.assertEqual(alert['type'], 'price')
        self.assertEqual(alert['message'], 'Test alert')
        self.assertEqual(alert['severity'], 'info')

    def test_get_alerts_by_severity(self):
        """Test filtering alerts by severity."""
        manager = AlertManager()
        
        manager.create_alert('test', 'Alert 1', 'info')
        manager.create_alert('test', 'Alert 2', 'warning')
        manager.create_alert('test', 'Alert 3', 'critical')
        
        warnings = manager.get_alerts(severity='warning')
        self.assertEqual(len(warnings), 1)

    def test_acknowledge_alert(self):
        """Test acknowledging alerts."""
        manager = AlertManager()
        
        alert = manager.create_alert('test', 'Test alert')
        manager.acknowledge_alert(alert['id'])
        
        alerts = manager.get_alerts(acknowledged=True)
        self.assertEqual(len(alerts), 1)


if __name__ == '__main__':
    unittest.main()
