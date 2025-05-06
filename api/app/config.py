import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
db_name = "tsimiguno"
users_collection_name = "users"
words_collection_name = "words"
candidates_count = 10
ui_origin = os.getenv("UI_ORIGIN")