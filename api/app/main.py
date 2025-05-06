from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from . import mongo
from . import config
from .letters import generate_word, to_disp_word, is_valid_word
from .learn import pick_candidates, create_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.ui_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), config.google_client_id)
        return idinfo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_info = verify_google_token(token)
    return user_info

@app.get("/candidates")
def get_candidates(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    model = mongo.load_model(user_id)
    if not model:
        words = [to_disp_word(generate_word()) for _ in range(config.candidates_count)]
        return words
    words = pick_candidates(config.candidates_count, model)
    return words

@app.post("/eval")
def update_model(words: dict[str, float], user: dict = Depends(get_current_user)):
    words = {k:v for k,v in words.items() if is_valid_word(k)}
    user_id = user["sub"]
    all_words = {**mongo.get_all_words(user_id), **words}
    if len(set(words.values())) > 1:
        model = create_model(list(all_words.items()))
        mongo.save_model(user_id, model)
    mongo.add_words(words, user_id)
    next_words = pick_candidates(config.candidates_count, model)
    return next_words
    
@app.get("/favorites")
def get_favorites(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    words = mongo.get_favorite_words(user_id)
    return words