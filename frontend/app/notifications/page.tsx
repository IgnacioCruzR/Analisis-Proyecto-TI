'use client'

import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { KPICard, KPICardSkeleton } from '@/components/dashboard/kpi-card'
import { ChartCard, ChartCardSkeleton } from '@/components/dashboard/chart-card'
import {
  useNotificationKPIs,
  useNotificationChannels,
  useNotificationStatus,
  useNotificationTimeline,
} from '@/hooks/use-analytics'
import {
  Bell,
  Mail,
  MessageSquare,
  Smartphone,
  CheckCircle,
  XCircle,
  ArrowLeftRight,
  Send,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// ── types que vienen del backend ──────────────────────────────────────────────
// GET /kpis/notifications/kpis
interface NotificationKPIsResponse {
  total_notifications: number
  delivered_notifications: number
  failed_notifications: number
  fallback_notifications: number
  failure_rate: number       // %
  delivery_rate: number      // % — equivale al "uptime del servicio"
  backpressure_ratio: number // %
  avg_attempts: number
}

// GET /kpis/notifications/channels
interface ChannelMetric {
  canal: string              // "sms" | "email" | "push"
  total: number
  delivered: number
  failed: number
  fallbacks: number
  avg_attempts: number
  delivery_rate: number      // %
  failure_rate: number       // %
}

// GET /kpis/notifications/status
interface StatusMetric {
  estado: string             // "enviado" | "entregado" | "fallido"
  count: number
  percentage: number
}

// GET /kpis/notifications/timeline
interface TimelinePoint {
  date: string
  total: number
  delivered: number
  failed: number
  fallbacks: number
}

// ── helpers ───────────────────────────────────────────────────────────────────
const CANAL_LABELS: Record<string, string> = {
  sms:   'SMS',
  email: 'Email',
  push:  'Push',
}

const CANAL_ICONS: Record<string, React.ReactNode> = {
  email: <Mail className="h-5 w-5" />,
  sms:   <MessageSquare className="h-5 w-5" />,
  push:  <Smartphone className="h-5 w-5" />,
}

const ESTADO_LABELS: Record<string, string> = {
  enviado:   'Enviado',
  entregado: 'Entregado',
  fallido:   'Fallido',
}

const ESTADO_COLORS: Record<string, string> = {
  enviado:   'var(--chart-2)',
  entregado: 'var(--chart-1)',
  fallido:   'var(--destructive)',
}

const CHANNEL_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
]

// ── page ──────────────────────────────────────────────────────────────────────
export default function NotificationsPage() {
  const { data: kpis,     isLoading: kpisLoading }     = useNotificationKPIs()
  const { data: channels, isLoading: channelsLoading } = useNotificationChannels()
  const { data: statuses, isLoading: statusesLoading } = useNotificationStatus()
  const { data: timeline, isLoading: timelineLoading } = useNotificationTimeline()

  // Adaptar canal para el BarChart (necesita key "channel" para el dataKey)
  const channelsForChart = channels?.map((c: ChannelMetric) => ({
    ...c,
    channel: CANAL_LABELS[c.canal] ?? c.canal,
  })) ?? []

  return (
    <DashboardLayout>
      <div className="space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Notificaciones
          </h1>
          <p className="text-muted-foreground">
            Entrega multicanal y rendimiento del servicio
          </p>
        </div>

        {/* KPI Cards — 4 cards mapeadas directamente al backend */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {kpisLoading ? (
            Array.from({ length: 4 }).map((_, i) => <KPICardSkeleton key={i} />)
          ) : (
            <>
              <KPICard
                title="Total enviadas"
                value={kpis?.total_notifications ?? 0}
                icon={<Send className="h-5 w-5" />}
              />
              <KPICard
                title="Uptime del servicio"
                value={kpis?.delivery_rate ?? 0}
                format="percentage"
                icon={<CheckCircle className="h-5 w-5" />}
              />
              <KPICard
                title="Tasa de fallos"
                value={kpis?.failure_rate ?? 0}
                format="percentage"
                icon={<XCircle className="h-5 w-5" />}
              />
              <KPICard
                title="Backpressure ratio"
                value={kpis?.backpressure_ratio ?? 0}
                format="percentage"
                icon={<ArrowLeftRight className="h-5 w-5" />}
              />
            </>
          )}
        </div>

        {/* Timeline real del backend */}
        <ChartCard
          title="Volumen de notificaciones"
          description="Notificaciones diarias: enviadas, entregadas y fallidas"
        >
          {timelineLoading ? (
            <div className="h-[350px] animate-pulse rounded-lg bg-muted" />
          ) : (
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeline ?? []}>
                  <defs>
                    <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--chart-2)" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="var(--chart-2)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="deliveredGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--chart-1)" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis
                    dataKey="date"
                    stroke="var(--muted-foreground)"
                    fontSize={12}
                    tickFormatter={(v: string) => v.slice(5)} // "MM-DD"
                  />
                  <YAxis stroke="var(--muted-foreground)" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--popover)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: 'var(--foreground)' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    stroke="var(--chart-2)"
                    fill="url(#totalGrad)"
                    strokeWidth={2}
                    name="Enviadas"
                  />
                  <Area
                    type="monotone"
                    dataKey="delivered"
                    stroke="var(--chart-1)"
                    fill="url(#deliveredGrad)"
                    strokeWidth={2}
                    name="Entregadas"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </ChartCard>

        {/* Channel Performance + Channel Details */}
        <div className="grid gap-6 lg:grid-cols-2">

          {channelsLoading ? (
            <ChartCardSkeleton />
          ) : (
            <ChartCard
              title="Rendimiento por canal"
              description="Entregadas y fallidas por canal"
            >
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={channelsForChart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="channel" stroke="var(--muted-foreground)" fontSize={12} />
                    <YAxis stroke="var(--muted-foreground)" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--popover)',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                      }}
                      labelStyle={{ color: 'var(--foreground)' }}
                    />
                    <Bar dataKey="delivered" fill="var(--chart-1)" name="Entregadas" radius={[4,4,0,0]} />
                    <Bar dataKey="failed"    fill="var(--destructive)" name="Fallidas" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>
          )}

          {channelsLoading ? (
            <ChartCardSkeleton />
          ) : (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-base font-semibold text-foreground">
                  Detalle por canal
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {channels?.map((c: ChannelMetric, i: number) => (
                  <div
                    key={c.canal}
                    className="flex items-center justify-between rounded-lg border border-border/50 bg-muted/30 p-4"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="flex h-10 w-10 items-center justify-center rounded-lg"
                        style={{
                          backgroundColor: `${CHANNEL_COLORS[i]}20`,
                          color: CHANNEL_COLORS[i],
                        }}
                      >
                        {CANAL_ICONS[c.canal] ?? <Bell className="h-5 w-5" />}
                      </div>
                      <div>
                        <div className="font-medium text-foreground">
                          {CANAL_LABELS[c.canal] ?? c.canal}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {c.total.toLocaleString()} enviadas
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-success">
                        {c.delivery_rate.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">tasa de entrega</div>
                      {c.fallbacks > 0 && (
                        <div className="text-xs text-warning mt-0.5">
                          {c.fallbacks} fallbacks
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Status breakdown — viene de /notifications/status */}
        <ChartCard
          title="Resumen de estados"
          description="Distribución actual de notificaciones por estado"
        >
          {statusesLoading ? (
            <div className="h-24 animate-pulse rounded-lg bg-muted" />
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              {statuses?.map((s: StatusMetric) => (
                <div
                  key={s.estado}
                  className="rounded-lg border border-border bg-muted/30 p-4 text-center"
                >
                  <div
                    className="text-3xl font-bold"
                    style={{ color: ESTADO_COLORS[s.estado] ?? 'var(--foreground)' }}
                  >
                    {s.count.toLocaleString()}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {ESTADO_LABELS[s.estado] ?? s.estado}
                  </div>
                  <div
                    className="text-xs mt-1"
                    style={{ color: ESTADO_COLORS[s.estado] ?? 'var(--muted-foreground)' }}
                  >
                    {s.percentage.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </ChartCard>

      </div>
    </DashboardLayout>
  )
}
