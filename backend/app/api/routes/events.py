import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import EventCreate, EventCreateResponse
from app.services import create_event, is_transaction_token_unique
from app.etl.processors.order_processor import process_order_event
from app.etl.processors.subscription_processor import process_subscription_event
from app.etl.processors.payment_processor import process_payment_event


PAYMENT_EVENT_TYPES = {"intento_pago", "pago_exitoso", "pago_rechazado"}

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={
        400: {"description": "Invalid event data"},
        500: {"description": "Internal server error"}
    }
)


def _validate_payment_event(event: EventCreate, db: Session) -> None:
    if event.event_type not in PAYMENT_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Eventos de pagos válidos: intento_pago, pago_exitoso, pago_rechazado. "
                f"event_type recibido: {event.event_type}"
            )
        )

    transaction_token = event.payload.get("transaction_token")
    if not transaction_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_token es obligatorio para eventos de pagos"
        )

    try:
        uuid.UUID(str(transaction_token))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_token debe ser un UUID válido"
        )

    if not is_transaction_token_unique(db, str(transaction_token)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_token debe ser único y no puede haberse usado en otra transacción"
        )

    if event.event_type == "pago_rechazado":
        error_code = event.payload.get("error_code")
        if not error_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="error_code es obligatorio para eventos pago_rechazado"
            )


@router.post(
    "",
    response_model=EventCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo evento",
    description=(
        "Recibe un evento de cualquier dominio, lo almacena en raw_events y lo procesa "
        "automáticamente si es orders, subscriptions o payments. Para pagos se valida "
        "transaction_token único y error_code en pago_rechazado."
    )
)
async def create_event_endpoint(
    event: EventCreate,
    db: Session = Depends(get_db)
) -> EventCreateResponse:

    try:
        if event.source == "payments":
            _validate_payment_event(event, db)

        # 1. Guardar evento en raw_events
        db_event = create_event(db=db, event=event)
        
        # 2. Procesar automáticamente según el dominio
        if db_event.source == "orders":
            try:
                process_order_event(db, db_event)
                db.commit()
                print(f"✅ [AUTO-ETL] Evento {db_event.event_type} (orders) procesado automáticamente")
            except Exception as etl_error:
                print(f"⚠️  [AUTO-ETL-ORDERS] Error: {str(etl_error)}")
        
        elif db_event.source == "subscriptions":
            try:
                process_subscription_event(db, db_event)
                db.commit()
                print(f"✅ [AUTO-ETL] Evento {db_event.event_type} (subscriptions) procesado automáticamente")
            except Exception as etl_error:
                print(f"⚠️  [AUTO-ETL-SUBSCRIPTIONS] Error: {str(etl_error)}")

        elif db_event.source == "payments":
            try:
                process_payment_event(db, db_event)
                db.commit()
                print(f"✅ [AUTO-ETL] Evento {db_event.event_type} (payments) procesado automáticamente")
            except Exception as etl_error:
                print(f"⚠️  [AUTO-ETL-PAYMENTS] Error: {str(etl_error)}")
        
        return EventCreateResponse(
            message="event stored",
            event_id=db_event.id,
            source=db_event.source,
            event_type=db_event.event_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el evento: {str(e)}"
        )
