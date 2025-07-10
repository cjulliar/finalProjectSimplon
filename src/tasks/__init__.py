"""
Module des tâches Celery pour l'automatisation des rapports bancaires.
"""

from .report_tasks import (
    generate_weekly_report,
    send_report_email,
    generate_and_send_report,
    cleanup_old_reports
)

__all__ = [
    'generate_weekly_report',
    'send_report_email', 
    'generate_and_send_report',
    'cleanup_old_reports'
] 