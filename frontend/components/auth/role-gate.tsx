'use client'

import { ShieldAlert } from 'lucide-react'
import type { ReactNode } from 'react'

import { useAuth } from '@/components/auth/auth-provider'
import { canAccess, type Domain } from '@/lib/roles'

interface RoleGateProps {
  /** Dominio definido en lib/roles.ts (overview, orders, salud, ...). */
  domain: Domain
  children: ReactNode
}

/**
 * Bloquea el acceso por URL directa a paginas que requieren un rol especifico.
 * Si el usuario no tiene rol valido, muestra un mensaje "Acceso denegado"
 * en lugar del contenido. Combinar con guards de backend (require_any_role).
 */
export function RoleGate({ domain, children }: RoleGateProps) {
  const { roles } = useAuth()

  if (canAccess(roles, domain)) {
    return <>{children}</>
  }

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-6">
      <div className="max-w-md rounded-lg border border-destructive/30 bg-destructive/5 p-6 text-center">
        <ShieldAlert className="mx-auto mb-3 h-10 w-10 text-destructive" />
        <h2 className="mb-1 text-lg font-semibold text-foreground">
          Acceso denegado
        </h2>
        <p className="text-sm text-muted-foreground">
          Tu usuario no tiene permiso para ver este dashboard. Si crees que es
          un error, pide a un administrador que te asigne el rol correspondiente
          en Keycloak.
        </p>
        <p className="mt-3 text-xs text-muted-foreground">
          Roles asignados: {roles.length > 0 ? roles.join(', ') : '(ninguno)'}
        </p>
      </div>
    </div>
  )
}
