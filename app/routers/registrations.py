from fastapi import APIRouter, Path, HTTPException, Query

from app.models.registration import Registration

from typing import Annotated
from app.data.db import SessionDep
from sqlmodel import select, delete
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.get("/")
def get_all_registrations(
    session : SessionDep,    #aggiungiamo la dipendenza per la sessione del database
    sort: Annotated[bool, Path(description="Sort the registrations by event_id", examples="True")] = False,
) -> list[Registration]:    
    """
    Restituisce una lista contenente tutte le registrazioni presenti nel database. 
    Se il parametro `sort` è impostato su `True`, la lista sarà ordinata in base al campo event_id.
    """
    registrations = session.exec(select(Registration)).all() #recupera tutte le registrazioni dal database
    if sort:
        registrations = sorted(registrations, key=lambda reg: reg.event_id)
    return list(registrations)

@router.delete("/")
def delete_registration(
    session: SessionDep,
    username: Annotated[str, Query(description="Username dell'utente registrato")],
    event_id: Annotated[int, Query(description="ID dell'evento")],
):
    """
    Elimina una singola registrazione identificata da username ed event_id.
    Se la registrazione non esiste, restituisce 404.
    """

    registration = session.exec(
        select(Registration).where(
            Registration.username == username,
            Registration.event_id == event_id
        )
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="Registrazione non trovata")

    session.delete(registration)
    session.commit()

    return {"message": "Registrazione cancellata con successo"}