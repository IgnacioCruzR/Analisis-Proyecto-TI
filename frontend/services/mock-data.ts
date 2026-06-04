import type {
  OrdersKPIs,
  OrderChannel,
  OrderStatus,
  OrderTimeline,
  SubscriptionKPIs,
  SubscriptionTimeline,
  NotificationKPIs,
  NotificationChannel,
  IoTKPIs,
  IoTDevice,
  IoTAlert,
  IncidentKPIs,
  IncidentTimeline,
  Incident,
  PaymentKPIs,
  PaymentTimeline,
  LogisticsKPIs,
  Route,
  ServiceStatus,
  Activity,
  Alert,
  RetentionRates,
  SubscriptionTimelineResponse,
  InventoryKPIs,
  WarehouseCapacity,
  LowStockItem,
  StockStatusSummary,
  LocationsCatalogResponse,
  ProductsThresholdsResponse,
  PaymentFailuresResponse,
  PaymentConciliationResponse,
  CRMKPIs,
  CRMTimeline,
  CRMTicketsResponse,
  CRMSLASummary,
} from "@/types/analytics";

// Orders Mock Data
export const ordersKPIs: OrdersKPIs = {
  totalOrders: 15847,
  deliveryRate: 94.2,
  revenue: 1284500,
  avgOrderValue: 81.05,
  slaCompliance: 97.8,
  pendingOrders: 234,
};

export const orderChannels: OrderChannel[] = [
  { name: "Web", value: 6420, percentage: 40.5 },
  { name: "Mobile App", value: 5280, percentage: 33.3 },
  { name: "API", value: 2847, percentage: 18.0 },
  { name: "POS", value: 1300, percentage: 8.2 },
];

export const orderStatuses: OrderStatus[] = [
  { status: "Delivered", count: 14930, color: "var(--chart-1)" },
  { status: "In Transit", count: 512, color: "var(--chart-2)" },
  { status: "Processing", count: 234, color: "var(--chart-3)" },
  { status: "Failed", count: 171, color: "var(--chart-5)" },
];

export const orderTimeline: OrderTimeline[] = Array.from(
  { length: 30 },
  (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (29 - i));
    const orders = Math.floor(400 + Math.random() * 200);
    return {
      date: date.toISOString().split("T")[0],
      orders,
      delivered: Math.floor(orders * (0.92 + Math.random() * 0.06)),
      failed: Math.floor(orders * (0.01 + Math.random() * 0.02)),
    };
  },
);

// Subscriptions Mock Data
export const subscriptionKPIs: SubscriptionKPIs = {
  activeSubscriptions: 8452,
  renewalRate: 87.3,
  churn: 2.8,
  monthlyRevenue: 423600,
  autoserviceRate: 76.5,
  newSubscriptions: 342,
};

export const subscriptionTimeline: SubscriptionTimelineResponse = {
  start_date: new Date(new Date().setMonth(new Date().getMonth() - 11))
    .toISOString()
    .slice(0, 7),
  end_date: new Date().toISOString().slice(0, 7),
  total_subscriptions: Math.floor(8000 + Math.random() * 500),
  timeline: Array.from({ length: 12 }, (_, i) => {
    const date = new Date();
    date.setMonth(date.getMonth() - (11 - i));
    return {
      date: date.toISOString().slice(0, 7),
      renewals: Math.floor(600 + Math.random() * 200),
      cancellations: Math.floor(50 + Math.random() * 50),
      new_subscriptions: Math.floor(200 + Math.random() * 150),
    };
  }),
};

export const retentionRates: RetentionRates = {
  retention_rates: {
    ["90_days"]: 78.5,
    ["30_days"]: 85.2,
    annual: 65.4,
  },
};
// Notifications Mock Data
export const notificationKPIs: NotificationKPIs = {
  totalSent: 892450,
  deliveryRate: 98.7,
  failureRate: 1.3,
  uptime: 99.95,
  avgLatency: 145,
};

export const notificationChannels: NotificationChannel[] = [
  { channel: "Email", sent: 425000, delivered: 419750, failed: 5250 },
  { channel: "SMS", sent: 287000, delivered: 283290, failed: 3710 },
  { channel: "Push", sent: 156000, delivered: 154440, failed: 1560 },
  { channel: "WhatsApp", sent: 24450, delivered: 24206, failed: 244 },
];

// IoT Mock Data
export const iotKPIs: IoTKPIs = {
  activeSensors: 1247,
  totalAlerts: 89,
  avgLatency: 23,
  invalidPackets: 0.02,
  uptime: 99.8,
};

export const iotDevices: IoTDevice[] = [
  {
    id: "IOT-001",
    name: "Temperature Sensor A1",
    status: "online",
    lastSeen: "2 min ago",
    batteryLevel: 87,
  },
  {
    id: "IOT-002",
    name: "Humidity Sensor B2",
    status: "online",
    lastSeen: "1 min ago",
    batteryLevel: 92,
  },
  {
    id: "IOT-003",
    name: "Motion Detector C3",
    status: "warning",
    lastSeen: "15 min ago",
    batteryLevel: 23,
  },
  {
    id: "IOT-004",
    name: "Pressure Sensor D4",
    status: "online",
    lastSeen: "3 min ago",
    batteryLevel: 78,
  },
  {
    id: "IOT-005",
    name: "GPS Tracker E5",
    status: "offline",
    lastSeen: "2 hours ago",
    batteryLevel: 0,
  },
];

export const iotAlerts: IoTAlert[] = [
  {
    id: "ALT-001",
    deviceId: "IOT-003",
    type: "Low Battery",
    severity: "warning",
    message: "Battery below 25%",
    timestamp: "10 min ago",
  },
  {
    id: "ALT-002",
    deviceId: "IOT-005",
    type: "Device Offline",
    severity: "critical",
    message: "Device not responding",
    timestamp: "2 hours ago",
  },
  {
    id: "ALT-003",
    deviceId: "IOT-001",
    type: "Temperature Alert",
    severity: "warning",
    message: "Temperature exceeds threshold",
    timestamp: "30 min ago",
  },
];

// Incidents Mock Data
export const incidentKPIs: IncidentKPIs = {
  activeIncidents: 12,
  resolvedToday: 8,
  avgResolutionTime: 2.4,
  slaCompliance: 94.5,
  criticalCount: 2,
};

export const incidentTimeline: IncidentTimeline[] = Array.from(
  { length: 14 },
  (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (13 - i));
    return {
      date: date.toISOString().split("T")[0],
      opened: Math.floor(5 + Math.random() * 10),
      resolved: Math.floor(4 + Math.random() * 12),
      critical: Math.floor(Math.random() * 3),
    };
  },
);

export const incidents: Incident[] = [
  {
    id: "INC-001",
    title: "Payment Gateway Timeout",
    severity: "critical",
    status: "investigating",
    assignee: "John D.",
    createdAt: "2 hours ago",
    updatedAt: "30 min ago",
  },
  {
    id: "INC-002",
    title: "High API Latency",
    severity: "high",
    status: "open",
    assignee: "Sarah M.",
    createdAt: "4 hours ago",
    updatedAt: "1 hour ago",
  },
  {
    id: "INC-003",
    title: "Email Delivery Delays",
    severity: "medium",
    status: "investigating",
    assignee: "Mike R.",
    createdAt: "6 hours ago",
    updatedAt: "2 hours ago",
  },
  {
    id: "INC-004",
    title: "Database Connection Pool",
    severity: "critical",
    status: "open",
    assignee: "Lisa K.",
    createdAt: "1 hour ago",
    updatedAt: "45 min ago",
  },
  {
    id: "INC-005",
    title: "CDN Cache Miss Rate",
    severity: "low",
    status: "resolved",
    assignee: "Tom H.",
    createdAt: "8 hours ago",
    updatedAt: "3 hours ago",
  },
];

// Payments Mock Data
export const paymentKPIs: PaymentKPIs = {
  totalTransactions: 45892,
  failedPayments: 412,
  failureRate: 0.9,
  revenue: 3245800,
  avgTransactionValue: 70.72,
  uptime: 99.99,
};

export const paymentTimeline: PaymentTimeline[] = Array.from(
  { length: 24 },
  (_, i) => {
    const date = new Date();
    date.setHours(date.getHours() - (23 - i));
    const successful = Math.floor(1500 + Math.random() * 500);
    return {
      date: `${date.getHours()}:00`,
      successful,
      failed: Math.floor(successful * (0.005 + Math.random() * 0.01)),
      amount: successful * (60 + Math.random() * 30),
    };
  },
);

export const paymentFailures: PaymentFailuresResponse = {
  rejection_rate: 2.1,
  total:          45892,
  failed:         964,
  reasons: [
    { reason: "Fondos insuficientes",       count: 434, percentage: 45.0 },
    { reason: "Tarjeta rechazada",          count: 230, percentage: 23.9 },
    { reason: "Timeout del proveedor",      count: 169, percentage: 17.5 },
    { reason: "Error de validación",        count: 131, percentage: 13.6 },
  ],
}

export const paymentConciliation: PaymentConciliationResponse = {
  statuses: [
    { status: "Aprobado",                    count: 44820, percentage: 97.7 },
    { status: "esperando_revisión",          count: 660,   percentage: 1.4  },
    { status: "discrepancia_de_monto",       count: 298,   percentage: 0.6  },
    { status: "discrepancia_de_transacciones", count: 114, percentage: 0.3  },
  ],
  total:         45892,
  approval_rate: 97.66,
}

// Logistics Mock Data
export const logisticsKPIs: LogisticsKPIs = {
  activeRoutes: 128,
  onTimeDelivery: 91.2,
  avgDeliveryTime: 42,
  pendingDeliveries: 567,
  driversActive: 89,
};

export const routes: Route[] = [
  {
    id: "RT-001",
    driver: "Carlos M.",
    status: "active",
    deliveries: 12,
    completed: 8,
    eta: "14:30",
  },
  {
    id: "RT-002",
    driver: "Ana P.",
    status: "active",
    deliveries: 15,
    completed: 12,
    eta: "15:45",
  },
  {
    id: "RT-003",
    driver: "Luis G.",
    status: "delayed",
    deliveries: 10,
    completed: 4,
    eta: "16:20",
  },
  {
    id: "RT-004",
    driver: "Maria S.",
    status: "completed",
    deliveries: 8,
    completed: 8,
    eta: "Done",
  },
  {
    id: "RT-005",
    driver: "Pedro R.",
    status: "active",
    deliveries: 14,
    completed: 7,
    eta: "15:00",
  },
];

// Service Status
export const serviceStatuses: ServiceStatus[] = [
  { name: "Orders Service", status: "operational", uptime: 99.98 },
  {
    name: "Payments Gateway",
    status: "degraded",
    uptime: 99.85,
    lastIncident: "2 hours ago",
  },
  { name: "Notifications", status: "operational", uptime: 99.95 },
  { name: "IoT Platform", status: "operational", uptime: 99.9 },
  { name: "CRM Service", status: "operational", uptime: 99.99 },
  { name: "Logistics Engine", status: "operational", uptime: 99.92 },
  { name: "Auth Service", status: "operational", uptime: 99.99 },
  { name: "Analytics Pipeline", status: "operational", uptime: 99.87 },
];

// Recent Activity
export const recentActivities: Activity[] = [
  {
    id: "ACT-001",
    type: "order",
    message: "New bulk order received from Enterprise Client",
    timestamp: "2 min ago",
    status: "success",
  },
  {
    id: "ACT-002",
    type: "payment",
    message: "Payment reconciliation completed for batch #4521",
    timestamp: "5 min ago",
    status: "success",
  },
  {
    id: "ACT-003",
    type: "incident",
    message: "High latency detected in payment gateway",
    timestamp: "15 min ago",
    status: "warning",
  },
  {
    id: "ACT-004",
    type: "notification",
    message: "SMS campaign sent to 15,000 subscribers",
    timestamp: "22 min ago",
    status: "success",
  },
  {
    id: "ACT-005",
    type: "iot",
    message: "Sensor IOT-003 battery critically low",
    timestamp: "30 min ago",
    status: "warning",
  },
  {
    id: "ACT-006",
    type: "order",
    message: "500 orders processed in last hour",
    timestamp: "45 min ago",
    status: "success",
  },
  {
    id: "ACT-007",
    type: "incident",
    message: "Database connection pool exhausted",
    timestamp: "1 hour ago",
    status: "error",
  },
];

// Critical Alerts
export const criticalAlerts: Alert[] = [
  {
    id: "CRT-001",
    title: "Payment Gateway Issues",
    message: "Increased failure rate detected",
    severity: "critical",
    source: "Payments",
    timestamp: "15 min ago",
  },
  {
    id: "CRT-002",
    title: "Database Connection Pool",
    message: "Pool utilization at 95%",
    severity: "critical",
    source: "Infrastructure",
    timestamp: "1 hour ago",
  },
  {
    id: "CRT-003",
    title: "IoT Device Offline",
    message: "GPS Tracker E5 not responding",
    severity: "warning",
    source: "IoT",
    timestamp: "2 hours ago",
  },
];

// ─── Inventory Mock Data ──────────────────────────────────────────────────────

export const inventoryKPIs: InventoryKPIs = {
  total_skus:         28456,
  total_stock_value:  4250000,
  warehouses_count:   4,
  low_stock_count:    24,
  out_of_stock_count: 3,
  turnover_rate:      4.2,
}

export const warehouseCapacity: WarehouseCapacity[] = [
  {
    location_id:   '00000000-0000-0000-0000-000000000001',
    location_code: 'BODEGA-SCL-01',
    location_name: 'Bodega Central Santiago',
    location_type: 'WAREHOUSE',
    city:          'Santiago',
    stock:         8540,
    capacity:      10000,
    utilization:   85.4,
  },
  {
    location_id:   '00000000-0000-0000-0000-000000000002',
    location_code: 'BODEGA-VLP-01',
    location_name: 'Bodega Valparaíso',
    location_type: 'WAREHOUSE',
    city:          'Valparaíso',
    stock:         6230,
    capacity:      8000,
    utilization:   77.9,
  },
  {
    location_id:   '00000000-0000-0000-0000-000000000004',
    location_code: 'DC-NORTE-01',
    location_name: 'CD Norte Antofagasta',
    location_type: 'DISTRIBUTION_CENTER',
    city:          'Antofagasta',
    stock:         4120,
    capacity:      6000,
    utilization:   68.7,
  },
  {
    location_id:   '00000000-0000-0000-0000-000000000005',
    location_code: 'DC-SUR-01',
    location_name: 'CD Sur Concepción',
    location_type: 'DISTRIBUTION_CENTER',
    city:          'Concepción',
    stock:         9200,
    capacity:      12000,
    utilization:   76.7,
  },
]

export const lowStockItems: LowStockItem[] = [
  {
    sku_id:                'SKU-MECH-001',
    product_name:          'Widget Pro',
    category:              'Partes mecánicas',
    unit:                  'unidad',
    critical_threshold:    50,
    total_available_stock: 12,
    total_physical_stock:  15,
    total_reserved_stock:  3,
    locations_count:       2,
    is_out_of_stock:       false,
    last_updated:          '2026-05-28T08:30:00Z',
  },
  {
    sku_id:                'SKU-ELEC-042',
    product_name:          'Connector A',
    category:              'Componentes electrónicos',
    unit:                  'unidad',
    critical_threshold:    30,
    total_available_stock: 8,
    total_physical_stock:  8,
    total_reserved_stock:  0,
    locations_count:       1,
    is_out_of_stock:       false,
    last_updated:          '2026-05-28T07:15:00Z',
  },
  {
    sku_id:                'SKU-ELEC-089',
    product_name:          'Sensor Module T200',
    category:              'Componentes electrónicos',
    unit:                  'unidad',
    critical_threshold:    25,
    total_available_stock: 0,
    total_physical_stock:  0,
    total_reserved_stock:  0,
    locations_count:       1,
    is_out_of_stock:       true,
    last_updated:          '2026-05-28T06:00:00Z',
  },
  {
    sku_id:                'SKU-TOOL-156',
    product_name:          'Power Unit B12',
    category:              'Herramientas',
    unit:                  'unidad',
    critical_threshold:    40,
    total_available_stock: 15,
    total_physical_stock:  20,
    total_reserved_stock:  5,
    locations_count:       2,
    is_out_of_stock:       false,
    last_updated:          '2026-05-27T23:45:00Z',
  },
  {
    sku_id:                'SKU-CHEM-003',
    product_name:          'Lubricante Industrial LX',
    category:              'Insumos químicos',
    unit:                  'litro',
    critical_threshold:    20,
    total_available_stock: 0,
    total_physical_stock:  0,
    total_reserved_stock:  0,
    locations_count:       1,
    is_out_of_stock:       true,
    last_updated:          '2026-05-28T05:30:00Z',
  },
]

export const stockStatusSummary: StockStatusSummary[] = [
  { status: 'NORMAL',       count: 28429, percentage: 99.9 },
  { status: 'CRITICAL',     count: 24,    percentage: 0.08 },
  { status: 'OUT_OF_STOCK', count: 3,     percentage: 0.01 },
]

export const locationsCatalog: LocationsCatalogResponse = {
  data: [
    {
      location_id:   '00000000-0000-0000-0000-000000000001',
      location_code: 'BODEGA-SCL-01',
      location_name: 'Bodega Central Santiago',
      location_type: 'WAREHOUSE',
      address:       'Av. Industrial 4500, Quilicura',
      city:          'Santiago',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-01-15T08:00:00Z',
    },
    {
      location_id:   '00000000-0000-0000-0000-000000000002',
      location_code: 'BODEGA-VLP-01',
      location_name: 'Bodega Valparaíso',
      location_type: 'WAREHOUSE',
      address:       'Ruta 68 Km 90',
      city:          'Valparaíso',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-02-01T09:00:00Z',
    },
    {
      location_id:   '00000000-0000-0000-0000-000000000003',
      location_code: 'BODEGA-SCL-02',
      location_name: 'Bodega Sur Santiago',
      location_type: 'WAREHOUSE',
      address:       'Camino a Melipilla 1200',
      city:          'Santiago',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-03-01T10:00:00Z',
    },
    {
      location_id:   '00000000-0000-0000-0000-000000000004',
      location_code: 'DC-NORTE-01',
      location_name: 'CD Norte Antofagasta',
      location_type: 'DISTRIBUTION_CENTER',
      address:       'Ruta 1 Norte Km 12',
      city:          'Antofagasta',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-03-10T10:00:00Z',
    },
    {
      location_id:   '00000000-0000-0000-0000-000000000005',
      location_code: 'DC-SUR-01',
      location_name: 'CD Sur Concepción',
      location_type: 'DISTRIBUTION_CENTER',
      address:       'Av. Industrial Sur 800',
      city:          'Concepción',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-04-01T08:30:00Z',
    },
    {
      location_id:   '00000000-0000-0000-0000-000000000008',
      location_code: 'RETAIL-RM-01',
      location_name: 'Tienda Providencia',
      location_type: 'RETAIL_POINT',
      address:       'Av. Providencia 1234, Local 5',
      city:          'Santiago',
      country:       'Chile',
      is_active:     true,
      created_at:    '2025-06-01T09:30:00Z',
    },
  ],
  total:        6,
  generated_at: new Date().toISOString(),
}

export const productsThresholds: ProductsThresholdsResponse = {
  data: [
    ...lowStockItems,
    {
      sku_id:                'SKU-PACK-201',
      product_name:          'Caja Corrugada 30x30',
      category:              'Embalaje',
      unit:                  'unidad',
      critical_threshold:    200,
      total_available_stock: 1450,
      total_physical_stock:  1500,
      total_reserved_stock:  50,
      locations_count:       3,
      is_below_threshold:    false,
      is_out_of_stock:       false,
      last_updated:          '2026-05-28T09:00:00Z',
    },
  ].map((item) => ({ ...item, is_below_threshold: (item as LowStockItem).total_available_stock <= (item as LowStockItem).critical_threshold })),
  total:                 6,
  total_below_threshold: 5,
  total_out_of_stock:    2,
  generated_at:          new Date().toISOString(),
}

// ─── CRM Mock Data ───────────────────────────────────────────────────────────

export const crmKPIs: CRMKPIs = {
  totalCustomers:         24856,
  openTickets:            142,
  avgResponseTimeMinutes: 18,
  csatScore:              4.7,
  messagesToday:          1245,
  resolutionRate:         94.5,
}

export const crmTimeline: CRMTimeline = {
  days: 14,
  points: Array.from({ length: 14 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (13 - i))
    return {
      date:     d.toISOString().split('T')[0],
      opened:   Math.floor(80 + Math.random() * 40),
      resolved: Math.floor(75 + Math.random() * 45),
    }
  }),
}

export const crmTickets: CRMTicketsResponse = {
  tickets: [
    { ticketId: 'TKT-4521', asunto: 'Problema con pago de suscripción', estado: 'abierto',       prioridad: 'alta',  canal: 'email',   sourceProject: 'pagos',      openedAt: new Date(Date.now() - 10 * 60000).toISOString(),  updatedAt: new Date(Date.now() - 10 * 60000).toISOString() },
    { ticketId: 'TKT-4520', asunto: 'No puede acceder a su cuenta',     estado: 'en_progreso',   prioridad: 'media', canal: 'chat',    sourceProject: 'auth',       openedAt: new Date(Date.now() - 25 * 60000).toISOString(),  updatedAt: new Date(Date.now() - 20 * 60000).toISOString() },
    { ticketId: 'TKT-4519', asunto: 'Solicitud: exportar a CSV',        estado: 'abierto',       prioridad: 'baja',  canal: 'portal',  sourceProject: 'analytics',  openedAt: new Date(Date.now() - 60 * 60000).toISOString(),  updatedAt: new Date(Date.now() - 60 * 60000).toISOString() },
    { ticketId: 'TKT-4518', asunto: 'Integración no funciona',          estado: 'cerrado',       prioridad: 'alta',  canal: 'email',   sourceProject: 'inventario', openedAt: new Date(Date.now() - 120 * 60000).toISOString(), updatedAt: new Date(Date.now() - 30 * 60000).toISOString() },
    { ticketId: 'TKT-4517', asunto: 'Error al generar reporte mensual', estado: 'en_progreso',   prioridad: 'media', canal: 'telefono',sourceProject: 'orders',     openedAt: new Date(Date.now() - 180 * 60000).toISOString(), updatedAt: new Date(Date.now() - 45 * 60000).toISOString() },
  ],
}

export const crmSLA: CRMSLASummary = {
  totalViolations:    8,
  criticalViolations: 2,
  slaComplianceRate:  94.5,
}

// Global KPIs for Overview
export const globalKPIs = {
  totalOrders: ordersKPIs.totalOrders,
  deliveryRate: ordersKPIs.deliveryRate,
  revenue: paymentKPIs.revenue,
  notificationSuccessRate: notificationKPIs.deliveryRate,
  activeSubscriptions: subscriptionKPIs.activeSubscriptions,
  iotAlerts: iotKPIs.totalAlerts,
  incidentCount: incidentKPIs.activeIncidents,
  paymentFailureRate: paymentKPIs.failureRate,
};
