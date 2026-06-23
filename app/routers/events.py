from fastapi import APIRouter, Path, HTTPException, Query

from app.models.event import Event, EventCreate, EventPublic
from app.models.user import User, UserCreate, UserPublic
from app.models.registration import Registration

from typing import Annotated
from app.data.db import SessionDep
from sqlmodel import select, delete
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/events", tags=["events"]) # tutte le LODE AL LAINO che iniziano con /events saranno in questo router, e avranno il tag "events" per la documentazione

@router.get("/")
def get_all_events(
    session : SessionDep,    #aggiungiamo la dipendenza per la sessione del database
    sort: Annotated[bool, Path(description="Sort the events by id", examples="True")] = False,
) -> list[EventPublic]:    
    """
    Restituisce una lista contenente tutti gli eventi presenti nel database. 
    Se il parametro `sort` è impostato su `True`, la lista sarà ordinata in base al campo id.
    """
    events = session.exec(select(Event)).all() #recupera tutti gli eventi dal database
    if sort:
        events = sorted(events, key=lambda event: event.id)
    return list(events)


@router.post("/")
def add_event(
    event: EventCreate,
    session: SessionDep
) -> JSONResponse:
    """
    Aggiunge un nuovo evento al database.
    """
    new_event = Event.model_validate(event)  
    session.add(new_event)
    session.commit()
    return JSONResponse(status_code=201, 
                        content={"msg": "Evento creato con successo", "event_id": new_event.id},)


@router.get("/{event_id}")
def get_event_by_id(
    session : SessionDep,   
    event_id: Annotated[int, Path(description="ID dell'evento che vogliamo", examples=1)]
) -> JSONResponse:
    """
    Restituisce l'evento con l'ID specificato.
    Se l'evento non esiste, viene sollevata un'eccezione HTTP 404.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return JSONResponse(status_code=200, content={
        "title": event.title,
        "description": event.description,
        "date": event.date.isoformat(),
        "location": event.location,
        "id": event.id,
    })


@router.put("/{event_id}")
def update_event(
    session : SessionDep,    
    event_id: Annotated[int, Path(description="ID dell'evento che vogliamo aggiornare")],
    updated_event: EventCreate
):
    """
    Aggiorna l'evento con l'ID specificato.
    Se l'evento non esiste, viene sollevata un'eccezione HTTP 404.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    event.title = updated_event.title
    event.description = updated_event.description
    event.date = updated_event.date
    event.location = updated_event.location
    
    session.add(event)
    session.commit()
    
    return "Evento aggiornato con successo"    


@router.post("/{event_id}/register")
def register_user_to_event(
    session: SessionDep,
    event_id: Annotated[int, Path(description="ID dell'evento a cui vogliamo registrare l'utente")],
    user: UserCreate
)   -> JSONResponse:
    """
    Registra un utente a un evento specificato dall'ID.
    Se l'evento o l'utente non esistono, viene sollevata un'eccezione HTTP 404.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    existing_user = session.get(User, user.username)
    if not existing_user:
        new_user = User.model_validate(user)
        session.add(new_user)
        session.commit()
        existing_user = new_user

    existing_registration = session.exec(
        select(Registration).where(
            Registration.username == existing_user.username,
            Registration.event_id == event.id
        )
    ).first()
    if existing_registration:
        raise HTTPException(status_code=422, detail="Utente già registrato a questo evento")
    
    registration = Registration(username=existing_user.username, event_id=event.id)
    session.add(registration)
    session.commit()
    
    return JSONResponse(
        status_code=200, 
        content={
            "msg": "Utente registrato con successo all'evento",
            "event_id": event.id, 
        }
    )


@router.delete("/")
def delete_all_events(session: SessionDep) -> JSONResponse:
    """
    Elimina tutti gli eventi dal database.
    """
    session.exec(delete(Event))
    session.commit()
    return "Tutti gli eventi sono stati eliminati con successo"

@router.delete("/{event_id}")
def delete_events_by_id(
    session : SessionDep,    
    event_id: Annotated[int, Path(description="ID dell'evento che vogliamo cancellare")],
):
    """
    Elimina l'evento con l'ID specificato.
    Se l'evento non esiste, viene sollevata un'eccezione HTTP 404.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    session.exec(delete(Event).where(Event.id == event_id))
    session.commit()

    return "Evento cancellato con successo"
    














