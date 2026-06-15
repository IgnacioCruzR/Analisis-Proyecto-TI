// API Service - Using mock data for now, ready to connect to real endpoints
import * as mockData from "./mock-data";
import { getAccessToken } from "@/lib/keycloak";
import type {
  NotificationChannelsResponse,
  NotificationStatusResponse,
  NotificationTimelineResponse,
  PaymentTimeline,
  ServiceStatus,
  Activity,
  Alert,
  StockStatusSummary,
  WarehouseCapacity,
} from "@/types/analytics";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(
  /\/+$/,
  "",
);

if (!API_BASE_URL) {
  if (process.env.NODE_ENV === "development") {
    console.warn(
      "[api] NEXT_PUBLIC_API_URL is not set — all requests will return mock data. " +
        "Set NEXT_PUBLIC_API_URL in .env.local to connect to the real backend.",
    );
  } else {
    throw new Error(
      "[api] NEXT_PUBLIC_API_URL is not set. " +
        "Configure it in your deployment environment (see .env.local.example). " +
        "Without it, all dashboard data is served from static mock values.",
    );
  }
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly path: string,
  ) {
    super(`[api] ${status} ${path}`);
    this.name = "ApiError";
  }
}

// Several endpoints wrap their array payload in { data: T[] } in production but
// the mock returns a bare array. This helper unwraps both shapes without `any`.
function unwrapData<T>(d: { data: T[] } | T[]): T[] {
  return Array.isArray(d) ? d : d.data;
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
    if (process.env.NODE_ENV !== 'production') {
      if (response.status === 401 || response.status === 403) {
        console.info(`[api] ${response.status} ${path} (sin permiso)`);
      } else {
        console.error(`[api] Error ${response.status} en ${path}`);
      }
    }
    throw new ApiError(response.status, path);
  }
  return response.json();
}

// Orders API
export const ordersAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(`/v1/kpis/orders/kpis?days=${days}`, mockData.ordersKPIs),
  getChannels: (days: number = 30) =>
    fetchAPI(`/v1/kpis/orders/channels?days=${days}`, mockData.orderChannels),
  getStatuses: (days: number = 30) =>
    fetchAPI(`/v1/kpis/orders/status?days=${days}`, mockData.orderStatuses),
  getTimeline: (days: number = 30) =>
    fetchAPI(`/v1/kpis/orders/timeline?days=${days}`, mockData.orderTimeline),
};

// Subscriptions API
export const subscriptionsAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(
      `/v1/kpis/subscriptions/summary?days=${days}`,
      mockData.subscriptionKPIs,
    ),
  getTimeline: (days: number = 30) =>
    fetchAPI(
      `/v1/kpis/subscriptions/timeline?days=${days}`,
      mockData.subscriptionTimeline,
    ),
  getRetentionRates: () =>
    fetchAPI("/v1/kpis/subscriptions/retention", mockData.retentionRates),
};

// Notifications API
export const notificationsAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(
      `/v1/kpis/notifications/kpis?days=${days}`,
      mockData.notificationKPIs,
    ),

  getChannels: (days: number = 30) =>
    fetchAPI<NotificationChannelsResponse>(
      `/v1/kpis/notifications/channels?days=${days}`,
      {
        total_notifications: mockData.notificationChannels.length,
        channels: mockData.notificationChannels,
      },
    ).then((data) => data.channels),

  getStatus: (days: number = 30) =>
    fetchAPI<NotificationStatusResponse>(
      `/v1/kpis/notifications/status?days=${days}`,
      mockData.notificationStatus,
    ).then((data) => data.statuses),

  getTimeline: (days: number = 30) =>
    fetchAPI<NotificationTimelineResponse>(
      `/v1/kpis/notifications/timeline?days=${days}`,
      mockData.notificationTimeline,
    ).then((data) => data.timeline),
};

// IoT API
export const iotAPI = {
  getKPIs: (days: number = 30) =>
    fetchAPI(`/v1/kpis/iot/kpis?days=${days}`, mockData.iotKPIs),
  getDevices: (days: number = 30) =>
    fetchAPI(`/v1/kpis/iot/status?days=${days}`, mockData.iotDevices),
  getAlerts: (days: number = 30, limit: number = 50) =>
    fetchAPI(
      `/v1/kpis/iot/events?days=${days}&limit=${limit}`,
      mockData.iotAlerts,
    ),
  getSensorsByType: (days: number = 30) =>
    fetchAPI(`/v1/kpis/iot/by-type?days=${days}`, []),
  getTimeline: (days: number = 30) =>
    fetchAPI(`/v1/kpis/iot/timeline?days=${days}`, []),
};

// Incidents API
export const incidentsAPI = {
  getKPIs: () => fetchAPI("/v1/kpis/incidents/kpis", mockData.incidentKPIs),
  getTimeline: () =>
    fetchAPI("/v1/kpis/incidents/timeline?days=14", mockData.incidentTimeline),
  getList: () => fetchAPI("/v1/kpis/incidents/list", mockData.incidents),
};

// Payments API
export const paymentsAPI = {
  getKPIs: () => fetchAPI("/v1/analytics/payments/kpis", mockData.paymentKPIs),
  getTimeline: () =>
    fetchAPI<{ data: PaymentTimeline[] } | PaymentTimeline[]>(
      "/v1/analytics/payments/timeline",
      mockData.paymentTimeline,
    ).then(unwrapData),
  getFailures: (hours = 24, topN = 10) =>
    fetchAPI(
      `/v1/analytics/payments/failures?hours=${hours}&top_n=${topN}`,
      mockData.paymentFailures,
    ),
  getConciliation: (hours = 24) =>
    fetchAPI(
      `/v1/analytics/payments/conciliation?hours=${hours}`,
      mockData.paymentConciliation,
    ),
};

// Overview API
export const overviewAPI = {
  getGlobalKPIs: () => fetchAPI("/v1/kpis/overview/kpis", mockData.globalKPIs),
  getServiceStatuses: () =>
    fetchAPI<{ data: ServiceStatus[] } | ServiceStatus[]>(
      "/v1/kpis/overview/services",
      mockData.serviceStatuses,
    ).then(unwrapData),
  getRecentActivities: () =>
    fetchAPI<{ data: Activity[] } | Activity[]>(
      "/v1/kpis/overview/activities?limit=10",
      mockData.recentActivities,
    ).then(unwrapData),
  getCriticalAlerts: () =>
    fetchAPI<{ data: Alert[] } | Alert[]>(
      "/v1/kpis/overview/alerts?limit=10",
      mockData.criticalAlerts,
    ).then(unwrapData),
};

// CRM API
export const crmAPI = {
  getKPIs: () => fetchAPI("/v1/kpis/crm/kpis", mockData.crmKPIs),
  getTimeline: (days = 14) =>
    fetchAPI(`/v1/kpis/crm/timeline?days=${days}`, mockData.crmTimeline),
  getTickets: () => fetchAPI("/v1/kpis/crm/tickets", mockData.crmTickets),
  getSLA: () => fetchAPI("/v1/kpis/crm/sla", mockData.crmSLA),
};

// Inventory API
export const inventoryAPI = {
  getKPIs: () => fetchAPI("/v1/inventory/kpis", mockData.inventoryKPIs),
  getStockStatus: () =>
    fetchAPI<{ data: StockStatusSummary[] } | StockStatusSummary[]>(
      "/v1/inventory/stock-status",
      mockData.stockStatusSummary,
    ).then(unwrapData),
  getWarehouseCapacity: () =>
    fetchAPI<{ data: WarehouseCapacity[] } | WarehouseCapacity[]>(
      "/v1/inventory/snapshot",
      mockData.warehouseCapacity,
    ).then(unwrapData),
  getLowStockItems: () =>
    fetchAPI(
      "/v1/inventory/products/thresholds?below_threshold=true",
      mockData.lowStockItems,
    ),
  getLocationsCatalog: () =>
    fetchAPI(
      "/v1/inventory/locations/catalog",
      mockData.locationsCatalog,
    ),
  getProductsThresholds: (belowThreshold?: boolean) =>
    fetchAPI(
      `/v1/inventory/products/thresholds${belowThreshold !== undefined ? `?below_threshold=${belowThreshold}` : ""}`,
      mockData.productsThresholds,
    ),
};
