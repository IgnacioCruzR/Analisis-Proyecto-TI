// API Service - Using mock data for now, ready to connect to real endpoints
import * as mockData from "./mock-data";
import { getAccessToken } from "@/lib/keycloak";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(
  /\/+$/,
  "",
);

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly path: string,
  ) {
    super(`[api] ${status} ${path}`);
    this.name = "ApiError";
  }
}

// When API_BASE_URL is not set, returns fallback (offline / local dev without backend).
// When API_BASE_URL is configured, throws ApiError on any non-OK response or network
// failure so callers (SWR hooks, try/catch) can surface the error to the user instead
// of silently showing stale mock data.
async function fetchAPI<T>(endpoint: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) {
    return fallback;
  }

  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const token = await getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { headers });
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      console.info(`[api] ${response.status} ${path} (sin permiso)`);
    } else {
      console.error(`[api] Error ${response.status} en ${path}`);
    }
    throw new ApiError(response.status, path);
  }
  return response.json();
}

// Orders API
export const ordersAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(`/kpis/orders/kpis?days=${days}`, mockData.ordersKPIs),
  getChannels: (days: number = 30) =>
    fetchAPI(`/kpis/orders/channels?days=${days}`, mockData.orderChannels),
  getStatuses: (days: number = 30) =>
    fetchAPI(`/kpis/orders/status?days=${days}`, mockData.orderStatuses),
  getTimeline: (days: number = 30) =>
    fetchAPI(`/kpis/orders/timeline?days=${days}`, mockData.orderTimeline),
};

// Subscriptions API
export const subscriptionsAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(
      `/kpis/subscriptions/summary?days=${days}`,
      mockData.subscriptionKPIs,
    ),
  getTimeline: (days: number = 30) =>
    fetchAPI(
      `/kpis/subscriptions/timeline?days=${days}`,
      mockData.subscriptionTimeline,
    ),
  getRetentionRates: () =>
    fetchAPI("/kpis/subscriptions/retention", mockData.retentionRates),
};

// Notifications API
export const notificationsAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(
      `/kpis/notifications/kpis?days=${days}`,
      mockData.notificationKPIs,
    ),

  getChannels: (days: number = 30) =>
    fetchAPI(
      `/kpis/notifications/channels?days=${days}`,
      mockData.notificationChannels,
    ).then((data: any) => data?.channels ?? data),

  getStatus: (days: number = 30) =>
    fetchAPI(
      `/kpis/notifications/status?days=${days}`,
      mockData.notificationStatus,
    ).then((data: any) => data?.statuses ?? data),

  getTimeline: (days: number = 30) =>
    fetchAPI(
      `/kpis/notifications/timeline?days=${days}`,
      mockData.notificationTimeline,
    ).then((data: any) => data?.timeline ?? data),
};

// IoT API
export const iotAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(`/kpis/iot/kpis?days=${days}`, mockData.iotKPIs),
  getDevices: (days: number = 30) =>
    fetchAPI(`/kpis/iot/status?days=${days}`, mockData.iotDevices),
  getAlerts: (days: number = 30, limit: number = 50) =>
    fetchAPI(
      `/kpis/iot/events?days=${days}&limit=${limit}`,
      mockData.iotAlerts,
    ),
  getSensorsByType: (days: number = 30) =>
    fetchAPI(`/kpis/iot/by-type?days=${days}`, []),
  getTimeline: (days: number = 30) =>
    fetchAPI(`/kpis/iot/timeline?days=${days}`, []),
};

// Incidents API
export const incidentsAPI = {
  getKPIs: () => fetchAPI("/kpis/incidents/kpis", mockData.incidentKPIs),
  getTimeline: () =>
    fetchAPI("/kpis/incidents/timeline?days=14", mockData.incidentTimeline),
  getList: () => fetchAPI("/kpis/incidents/list", mockData.incidents),
};

// Payments API
export const paymentsAPI = {
  getKPIs: () => fetchAPI("/analytics/payments/kpis", mockData.paymentKPIs),
  getTimeline: () =>
    fetchAPI("/analytics/payments/timeline", mockData.paymentTimeline),
  getFailures: (hours = 24, topN = 10) =>
    fetchAPI(
      `/analytics/payments/failures?hours=${hours}&top_n=${topN}`,
      mockData.paymentFailures,
    ),
  getConciliation: (hours = 24) =>
    fetchAPI(
      `/analytics/payments/conciliation?hours=${hours}`,
      mockData.paymentConciliation,
    ),
};

// Overview API
export const overviewAPI = {
  getGlobalKPIs: () => fetchAPI("/kpis/overview/kpis", mockData.globalKPIs),
  getServiceStatuses: () =>
    fetchAPI("/kpis/overview/services", mockData.serviceStatuses),
  getRecentActivities: () =>
    fetchAPI("/kpis/overview/activities?limit=10", mockData.recentActivities),
  getCriticalAlerts: () =>
    fetchAPI("/kpis/overview/alerts?limit=10", mockData.criticalAlerts),
};

// CRM API
export const crmAPI = {
  getKPIs: () => fetchAPI("/kpis/crm/kpis", mockData.crmKPIs),
  getTimeline: (days = 14) =>
    fetchAPI(`/kpis/crm/timeline?days=${days}`, mockData.crmTimeline),
  getTickets: () => fetchAPI("/kpis/crm/tickets", mockData.crmTickets),
  getSLA: () => fetchAPI("/kpis/crm/sla", mockData.crmSLA),
};

// Inventory API
export const inventoryAPI = {
  getKPIs: () => fetchAPI("/inventory/kpis", mockData.inventoryKPIs),
  getStockStatus: () =>
    fetchAPI("/inventory/stock-status", mockData.stockStatusSummary).then(
      (data: any) => data?.data ?? data,
    ),
  getWarehouseCapacity: () =>
    fetchAPI("/inventory/snapshot", mockData.warehouseCapacity).then(
      (data: any) => data?.data ?? data,
    ),
  getLowStockItems: () =>
    fetchAPI(
      "/inventory/products/thresholds?below_threshold=true",
      mockData.lowStockItems,
    ),
  getLocationsCatalog: (locationType?: string) =>
    fetchAPI(
      `/inventory/locations/catalog${locationType ? `?location_type=${locationType}` : ""}`,
      mockData.locationsCatalog,
    ),
  getProductsThresholds: (belowThreshold?: boolean) =>
    fetchAPI(
      `/inventory/products/thresholds${belowThreshold !== undefined ? `?below_threshold=${belowThreshold}` : ""}`,
      mockData.productsThresholds,
    ),
};
