from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row._mapping)


# ============================================================================
#  §1  GET /inventory/snapshot
#      Último estado por (sku_id × location_id) desde fact_inventory_alerts
# ============================================================================

_SQL_SNAPSHOT_DATA = text("""
    WITH latest_alert AS (
        SELECT DISTINCT ON (sku_id, location_id)
            sku_id,
            location_id                                                     AS location_id,
            current_stock                                                   AS physical_stock,
            0                                                               AS reserved_stock,
            current_stock                                                   AS available_stock,
            threshold_limite                                                AS critical_threshold,
            is_stock_out,
            CASE
                WHEN is_stock_out = TRUE OR current_stock = 0 THEN 'OUT_OF_STOCK'
                WHEN current_stock <= threshold_limite         THEN 'CRITICAL'
                ELSE                                                'NORMAL'
            END                                                             AS stock_status,
            to_char(alert_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')               AS last_movement_at,
            to_char(ingested_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')            AS updated_at
        FROM fact_inventory_alerts
        ORDER BY sku_id, location_id, alert_at DESC
    )
    SELECT *
    FROM latest_alert
    WHERE (CAST(:sku_id AS TEXT)       IS NULL OR sku_id      = CAST(:sku_id AS TEXT))
    AND (CAST(:location_id AS TEXT)  IS NULL OR location_id = CAST(:location_id AS TEXT))
    AND (CAST(:stock_status AS TEXT) IS NULL OR stock_status = CAST(:stock_status AS TEXT))
    ORDER BY sku_id ASC, location_id ASC
    LIMIT  :limit
    OFFSET :offset
""")

_SQL_SNAPSHOT_COUNT = text("""
    WITH latest_alert AS (
        SELECT DISTINCT ON (sku_id, location_id)
            sku_id,
            location_id,
            current_stock,
            threshold_limite,
            is_stock_out,
            CASE
                WHEN is_stock_out = TRUE OR current_stock = 0 THEN 'OUT_OF_STOCK'
                WHEN current_stock <= threshold_limite         THEN 'CRITICAL'
                ELSE                                                'NORMAL'
            END AS stock_status
        FROM fact_inventory_alerts
        ORDER BY sku_id, location_id, alert_at DESC
    )
    SELECT COUNT(*)
    FROM latest_alert
    WHERE (CAST(:sku_id AS TEXT)       IS NULL OR sku_id      = CAST(:sku_id AS TEXT))
    AND (CAST(:location_id AS TEXT)  IS NULL OR location_id = CAST(:location_id AS TEXT))
    AND (CAST(:stock_status AS TEXT) IS NULL OR stock_status = CAST(:stock_status AS TEXT))
""")


def get_inventory_snapshot(
    db:            Session,
    sku_id:        Optional[str],
    location_id:   Optional[str],
    location_type: Optional[str],  # no disponible sin tabla locations
    stock_status:  Optional[str],
    limit:         int,
    offset:        int,
) -> Tuple[List[Dict[str, Any]], int]:
    params = {
        "sku_id":       sku_id       or None,
        "location_id":  location_id  or None,
        "stock_status": stock_status or None,
        "limit":        limit,
        "offset":       offset,
    }
    total = db.execute(_SQL_SNAPSHOT_COUNT, params).scalar_one()
    rows  = db.execute(_SQL_SNAPSHOT_DATA,  params).fetchall()
    return [_row_to_dict(r) for r in rows], total


# ============================================================================
#  §2  GET /locations/catalog
#      Sin tabla locations — retorna ubicaciones únicas desde fact_inventory_alerts
# ============================================================================

_SQL_LOCATIONS = text("""
    SELECT DISTINCT
        location_id                                                         AS location_id,
        location_id                                                         AS location_code,
        location_id                                                         AS location_name,
        'WAREHOUSE'                                                         AS location_type,
        NULL                                                                AS address,
        NULL                                                                AS city,
        'Chile'                                                             AS country,
        TRUE                                                                AS is_active,
        to_char(MIN(ingested_at), 'YYYY-MM-DD"T"HH24:MI:SS"Z"')           AS created_at
    FROM fact_inventory_alerts
    WHERE location_id IS NOT NULL
    AND (CAST(:location_type AS TEXT) IS NULL OR 'WAREHOUSE' = CAST(:location_type AS TEXT))
    AND (CAST(:is_active AS BOOLEAN)  IS NULL OR CAST(:is_active AS BOOLEAN) = TRUE)
    AND (CAST(:city AS TEXT)          IS NULL)
    GROUP BY location_id
    ORDER BY location_id
""")


def get_locations_catalog(
    db:            Session,
    location_type: Optional[str],
    is_active:     Optional[bool],
    city:          Optional[str],
) -> List[Dict[str, Any]]:
    params = {
        "location_type": location_type or None,
        "is_active":     is_active,
        "city":          city or None,
    }
    rows = db.execute(_SQL_LOCATIONS, params).fetchall()
    return [_row_to_dict(r) for r in rows]


# ============================================================================
#  §3  GET /products/thresholds
#      Agrega por sku_id desde fact_inventory_alerts (último estado por ubicación)
# ============================================================================

_SQL_THRESHOLDS = text("""
    WITH latest_per_location AS (
        SELECT DISTINCT ON (sku_id, location_id)
            sku_id,
            location_id,
            current_stock,
            threshold_limite,
            is_stock_out,
            alert_at
        FROM fact_inventory_alerts
        ORDER BY sku_id, location_id, alert_at DESC
    ),
    stock_por_sku AS (
        SELECT
            sku_id,
            sku_id                                          AS product_name,
            'Sin categoría'                                 AS category,
            'unidad'                                        AS unit,
            MAX(threshold_limite)                           AS critical_threshold,
            SUM(current_stock)                              AS total_physical_stock,
            0                                               AS total_reserved_stock,
            SUM(current_stock)                              AS total_available_stock,
            COUNT(DISTINCT location_id)                     AS locations_count,
            to_char(MAX(alert_at), 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS last_updated
        FROM latest_per_location
        WHERE (CAST(:sku_id AS TEXT) IS NULL OR sku_id ILIKE '%' || CAST(:sku_id AS TEXT) || '%')
        GROUP BY sku_id
    )
    SELECT
        sku_id,
        product_name,
        category,
        unit,
        critical_threshold,
        total_physical_stock,
        total_reserved_stock,
        total_available_stock,
        locations_count,
        (total_available_stock <= critical_threshold)       AS is_below_threshold,
        (total_available_stock = 0)                         AS is_out_of_stock,
        last_updated
    FROM stock_por_sku
    WHERE CAST(:below_threshold AS BOOLEAN) IS NULL
    OR (CAST(:below_threshold AS BOOLEAN) = TRUE  AND total_available_stock <= critical_threshold)
    OR (CAST(:below_threshold AS BOOLEAN) = FALSE AND total_available_stock >  critical_threshold)
    ORDER BY
        (total_available_stock = 0)                        DESC,
        (total_available_stock <= critical_threshold)      DESC,
        sku_id                                             ASC
""")


def get_products_thresholds(
    db:              Session,
    sku_id:          Optional[str],
    category:        Optional[str],
    below_threshold: Optional[bool],
) -> List[Dict[str, Any]]:
    params = {
        "sku_id":          sku_id or None,
        "category":        None,   # sin tabla products, ignoramos este filtro
        "below_threshold": below_threshold,
    }
    rows = db.execute(_SQL_THRESHOLDS, params).fetchall()
    return [_row_to_dict(r) for r in rows]


# ============================================================================
#  §4  GET /inventory/kpis
# ============================================================================

_SQL_KPI_SKUS = text("""
    WITH latest_per_location AS (
        SELECT DISTINCT ON (sku_id, location_id)
            sku_id,
            current_stock,
            threshold_limite
        FROM fact_inventory_alerts
        ORDER BY sku_id, location_id, alert_at DESC
    ),
    stock_por_sku AS (
        SELECT
            sku_id,
            SUM(current_stock)      AS total_available,
            MAX(threshold_limite)   AS threshold
        FROM latest_per_location
        GROUP BY sku_id
    )
    SELECT
        COUNT(*)                                              AS total_skus,
        COUNT(*) FILTER (WHERE total_available <= threshold)  AS low_stock_count,
        COUNT(*) FILTER (WHERE total_available = 0)           AS out_of_stock_count
    FROM stock_por_sku
""")

_SQL_KPI_WAREHOUSES = text("""
    SELECT COUNT(DISTINCT location_id) AS warehouses_count
    FROM fact_inventory_alerts
    WHERE location_id IS NOT NULL
""")


def get_inventory_kpis(db: Session) -> Dict[str, Any]:
    sku_row = db.execute(_SQL_KPI_SKUS).fetchone()
    wh_row  = db.execute(_SQL_KPI_WAREHOUSES).fetchone()
    return {
        "total_skus":         int(sku_row.total_skus)         if sku_row else 0,
        "total_stock_value":  0.0,
        "warehouses_count":   int(wh_row.warehouses_count)    if wh_row  else 0,
        "low_stock_count":    int(sku_row.low_stock_count)     if sku_row else 0,
        "out_of_stock_count": int(sku_row.out_of_stock_count)  if sku_row else 0,
        "turnover_rate":      0.0,
    }


# ============================================================================
#  §5  GET /inventory/stock-status
# ============================================================================

_SQL_STOCK_STATUS = text("""
    WITH latest_per_location AS (
        SELECT DISTINCT ON (sku_id, location_id)
            sku_id,
            current_stock,
            threshold_limite,
            is_stock_out
        FROM fact_inventory_alerts
        ORDER BY sku_id, location_id, alert_at DESC
    ),
    stock_por_sku AS (
        SELECT
            sku_id,
            SUM(current_stock)    AS total_available,
            MAX(threshold_limite) AS threshold,
            BOOL_OR(is_stock_out) AS any_stock_out
        FROM latest_per_location
        GROUP BY sku_id
    ),
    classified AS (
        SELECT
            CASE
                WHEN total_available = 0 OR any_stock_out THEN 'OUT_OF_STOCK'
                WHEN total_available <= threshold          THEN 'CRITICAL'
                ELSE                                           'NORMAL'
            END AS status
        FROM stock_por_sku
    ),
    totales AS (SELECT COUNT(*) AS n FROM classified)
    SELECT
        c.status,
        COUNT(*)                                             AS count,
        ROUND(100.0 * COUNT(*) / NULLIF(t.n, 0), 2)         AS percentage
    FROM classified c, totales t
    GROUP BY c.status, t.n
    ORDER BY
        CASE c.status
            WHEN 'OUT_OF_STOCK' THEN 1
            WHEN 'CRITICAL'     THEN 2
            ELSE                     3
        END
""")


def get_stock_status_summary(db: Session) -> Tuple[List[Dict[str, Any]], int]:
    rows = db.execute(_SQL_STOCK_STATUS).fetchall()
    data  = [_row_to_dict(r) for r in rows]
    total = sum(int(r["count"]) for r in data)
    return data, total