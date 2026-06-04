// API Service - Using mock data for now, ready to connect to real endpoints
import * as mockData from './mock-data'

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/+$/, '')

// Helper function for API calls (ready for real endpoints)
async function fetchAPI<T>(endpoint: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) {
    return fallback
  }

  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`

  try {
    const response = await fetch(`${API_BASE_URL}${path}`)
    if (!response.ok) throw new Error(`API Error ${response.status}`)
    return response.json()
  } catch (err) {
    console.warn(`Using mock data for ${path}:`, err)
    return fallback
  }
}

// Orders API
export const ordersAPI = {
  getKPIs: () => fetchAPI('/kpis/orders/kpis', mockData.ordersKPIs),
  getChannels: () => fetchAPI('/kpis/orders/channels', mockData.orderChannels),
  getStatuses: () => fetchAPI('/kpis/orders/status', mockData.orderStatuses),
  getTimeline: (days: number = 30) => fetchAPI(`/kpis/orders/timeline?days=${days}`, mockData.orderTimeline),
}

// Subscriptions API
export const subscriptionsAPI = {
  getKPIs: (days: number = 30) => fetchAPI(`/kpis/subscriptions/summary?days=${days}`, mockData.subscriptionKPIs),
  getTimeline: (days: number = 30) => fetchAPI(`/kpis/subscriptions/timeline?days=${days}`, mockData.subscriptionTimeline),
  getRetentionRates: () => fetchAPI('/kpis/subscriptions/retention', mockData.retentionRates),
}

// Notifications API
export const notificationsAPI = {
  getKPIs: () => fetchAPI('/analytics/notifications/kpis', mockData.notificationKPIs),
  getChannels: () => fetchAPI('/analytics/notifications/channels', mockData.notificationChannels),
}

// IoT API
export const iotAPI = {
  getKPIs: () => fetchAPI('/analytics/iot/kpis', mockData.iotKPIs),
  getDevices: () => fetchAPI('/analytics/iot/devices', mockData.iotDevices),
  getAlerts: () => fetchAPI('/analytics/iot/alerts', mockData.iotAlerts),
}

// Incidents API
export const incidentsAPI = {
  getKPIs: () => fetchAPI('/kpis/incidents/kpis', mockData.incidentKPIs),
  getTimeline: () => fetchAPI('/kpis/incidents/timeline?days=14', mockData.incidentTimeline),
  getList: () => fetchAPI('/kpis/incidents/list', mockData.incidents),
}

// Payments API
export const paymentsAPI = {
  getKPIs:          ()               => fetchAPI('/analytics/payments/kpis',                      mockData.paymentKPIs),
  getTimeline:      (hours = 24)     => fetchAPI(`/analytics/payments/timeline?hours=${hours}`,   mockData.paymentTimeline),
  getFailures:      (hours = 24, topN = 10) => fetchAPI(`/analytics/payments/failures?hours=${hours}&top_n=${topN}`, mockData.paymentFailures),
  getConciliation:  (hours = 24)     => fetchAPI(`/analytics/payments/conciliation?hours=${hours}`, mockData.paymentConciliation),
}

// Logistics API
export const logisticsAPI = {
  getKPIs: () => fetchAPI('/analytics/logistics/kpis', mockData.logisticsKPIs),
  getRoutes: () => fetchAPI('/analytics/logistics/routes', mockData.routes),
}

// Overview API
export const overviewAPI = {
  getGlobalKPIs: () => fetchAPI('/kpis/overview/kpis', mockData.globalKPIs),
  getServiceStatuses: () => fetchAPI('/kpis/overview/services', mockData.serviceStatuses),
  getRecentActivities: () => fetchAPI('/kpis/overview/activities?limit=10', mockData.recentActivities),
  getCriticalAlerts: () => fetchAPI('/kpis/overview/alerts?limit=10', mockData.criticalAlerts),
}

// CRM API
export const crmAPI = {
  getKPIs:    ()            => fetchAPI('/kpis/crm/kpis',              mockData.crmKPIs),
  getTimeline:(days = 14)   => fetchAPI(`/kpis/crm/timeline?days=${days}`, mockData.crmTimeline),
  getTickets: ()            => fetchAPI('/kpis/crm/tickets',           mockData.crmTickets),
  getSLA:     ()            => fetchAPI('/kpis/crm/sla',               mockData.crmSLA),
}

// Inventory API (Grupo 5 endpoints)
export const inventoryAPI = {
  getKPIs:             () => fetchAPI('/inventory/kpis',                           mockData.inventoryKPIs),
  getWarehouseCapacity:() => fetchAPI('/inventory/snapshot?limit=50',              mockData.warehouseCapacity),
  getLowStockItems:    () => fetchAPI('/products/thresholds?below_threshold=true', mockData.lowStockItems),
  getStockStatus:      () => fetchAPI('/inventory/stock-status',                   mockData.stockStatusSummary),
  getLocationsCatalog: (type?: string) =>
    fetchAPI(`/locations/catalog${type ? `?location_type=${type}` : ''}`,         mockData.locationsCatalog),
  getProductsThresholds:(belowThreshold?: boolean) =>
    fetchAPI(`/products/thresholds${belowThreshold != null ? `?below_threshold=${belowThreshold}` : ''}`, mockData.productsThresholds),
}
