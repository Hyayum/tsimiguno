import io
import joblib
import pymongo
import gridfs
from . import config

client = pymongo.MongoClient(config.mongo_uri)
db = client[config.db_name]
users_db = db[config.users_collection_name]
words_db = db[config.words_collection_name]
fs = gridfs.GridFS(db)

def add_user(user_id):
    users_db.insert_one({"user_id": user_id})

def add_words(words: dict[str, float], user_id):
    docs = [{"user_id": user_id, "word": k, "score": v, "created_at": db.command("serverStatus")["localTime"]} for k, v in words.items()]
    words_db.insert_many(docs)
    
def get_all_words(user_id):
    docs = words_db.find({"user_id": user_id})
    words_dict = {}
    for doc in docs:
        words_dict[doc["word"]] = doc["score"]
    return words_dict

def get_favorite_words(user_id):
    docs = words_db.find({"user_id": user_id, "score": 1})
    words = [doc["word"] for doc in docs]
    return words

def get_model_id(user_id):
    user = users_db.find_one({"user_id": user_id})
    if not user: return None
    file_id = user.get("model_id")
    return file_id

def save_model(user_id, model):
    old_file_id = get_model_id(user_id)
    buffer = io.BytesIO()
    joblib.dump(model, buffer)
    buffer.seek(0)
    file_id = fs.put(buffer, filename=f"model_{user_id}.pkl")
    users_db.update_one({"user_id": user_id}, {"$set": {"model_id": file_id, "model_updated_at": db.command("serverStatus")["localTime"]}}, upsert=True)
    if old_file_id:
        fs.delete(old_file_id)
    
def load_model(user_id):
    file_id = get_model_id(user_id)
    if not file_id: return None
    stored_file = fs.get(file_id)
    buffer = io.BytesIO(stored_file.read())
    buffer.seek(0)
    model = joblib.load(buffer)
    return model