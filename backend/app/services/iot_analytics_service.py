"""
IoT Analytics Service - Wrapper para funciones de analítica de IoT.

Re-exporta funciones desde app.analytics.iot_kpis para uso en endpoints y servicios.
"""

from app.analytics.iot_kpis import (
    get_total_sensors,
    get_online_sensors,
    get_offline_sensors,
    get_availability_rate,
    get_avg_battery_level,
    get_low_battery_count,
    get_data_validity_rate,
    get_anomalies_detected,
    get_avg_processing_latency_ms,
    get_all_iot_kpis,
    get_sensors_status,
    get_sensors_by_type,
    get_iot_events,
    get_iot_timeline,
    process_unprocessed_iot_events,
)

__all__ = [
    "get_total_sensors",
    "get_online_sensors",
    "get_offline_sensors",
    "get_availability_rate",
    "get_avg_battery_level",
    "get_low_battery_count",
    "get_data_validity_rate",
    "get_anomalies_detected",
    "get_avg_processing_latency_ms",
    "get_all_iot_kpis",
    "get_sensors_status",
    "get_sensors_by_type",
    "get_iot_events",
    "get_iot_timeline",
    "process_unprocessed_iot_events",
]
