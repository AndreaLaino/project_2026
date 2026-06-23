from fastapi import APIRouter, Path, HTTPException, Query

from app.models.user import User, UserCreate, UserPublic

from typing import Annotated
from app.data.db import SessionDep
from sqlmodel import select, delete
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["users"]) # tutte le LODE AL LAINO che iniziano con /users saranno in questo router, e avranno il tag "users" per la documentazione

@router.get("/")
def get_all_users(
    session : SessionDep,    #aggiungiamo la dipendenza per la sessione del database
    sort: Annotated[bool, Path(description="Sort the users by username", examples="True")] = False,
) -> list[UserPublic]:    
    """
    Restituisce una lista contenente tutti gli eventi presenti nel database. 
    Se il parametro `sort` è impostato su `True`, la lista sarà ordinata in base al campo username.
    """
    users = session.exec(select(User)).all() #recupera tutti gli utenti dal database
    if sort:
        users = sorted(users, key=lambda user: user.username)
    return list(users)


@router.post("/")
def add_user(
    user: UserCreate,
    session: SessionDep
) -> JSONResponse:
    """
    Aggiunge un nuovo utente al database.
    """
    if user.username in session.exec(select(User.username)).all():
        raise HTTPException(status_code=422, detail="Username già esistente")
    new_user = User.model_validate(user)
    session.add(new_user)
    session.commit()
    return JSONResponse(status_code=201, 
                        content={"msg": "Utente creato con successo", "user_id": new_user.username},)

@router.get("/{username}")
def get_user_by_username(
    session : SessionDep,   
    username: Annotated[str, Path(description="Username dell'utente che vogliamo", examples="john_pork")]
) -> JSONResponse:
    """
    Restituisce l'utente con il username specificato.
    Se l'utente non esiste, viene sollevata un'eccezione HTTP 404.
    """
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return JSONResponse(status_code=200, content={
        "username": user.username,
        "name": user.name,
        "email": user.email,
    })

@router.delete("/")
def delete_all_users(session: SessionDep) -> JSONResponse:
    """
    Elimina tutti gli utenti dal database.
    """
    session.exec(delete(User))
    session.commit()
    return "Tutti gli utenti sono stati eliminati con successo"

@router.delete("/{username}")
def delete_user_by_username(
    session : SessionDep,    
    username: Annotated[str, Path(description="Username dell'utente che vogliamo cancellare", examples="john_pork")],
):
    """
    Elimina l'utente con il username specificato.
    Se l'utente non esiste, viene sollevata un'eccezione HTTP 404.
    """
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    session.exec(delete(User).where(User.username == username))
    session.commit()

    return "Utente cancellato con successo"
    














