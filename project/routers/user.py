from fastapi import APIRouter, HTTPException,status
from ..models.user import UserIn
from ..security import get_user, get_password_hash
from ..database import user_table, database

router = APIRouter()

@router.post("/register", status_code=201)
async def create_user(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists"
        )
    
    # query = user_table.insert().values(email = user.email, password = user.password) Never insert plain password directly in the DB
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email = user.email, password = hashed_password)

    await database.execute(query=query)
    return {"detail" : "User Created."}