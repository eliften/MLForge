import os
from upstash_redis import Redis
import dotenv, base64, io
import pickle
import zlib

dotenv.load_dotenv()

def get_redis():
    return Redis(
        url=os.getenv("URL"),
        token=os.getenv("TOKEN")
    )

def save_df_to_redis(r, session_id, df, df_type):
    key = f"session:{session_id}:df:{df_type}"
    binary = pickle.dumps(df)
    compressed = zlib.compress(binary)
    encoded = base64.b64encode(compressed).decode("utf-8")

    r.setex(key, 7200, encoded)


def load_df_from_redis(r, session_id, df_type):
    key = f"session:{session_id}:df:{df_type}"
    encoded = r.get(key)

    if encoded is None:
        return None

    compressed = base64.b64decode(encoded)
    binary = zlib.decompress(compressed)

    return pickle.loads(binary)

def save_problem_type_to_redis(r, session_id, problem_type):
    key = f"session:{session_id}:problem_type"
    r.setex(key, 7200, problem_type)

def load_problem_type_from_redis(r, session_id):
    key = f"session:{session_id}:problem_type"
    value = r.get(key)
    return value

def save_model_to_redis(r, session_id, model_type):
    key = f"session:{session_id}:model"
    r.setex(key, 7200, model_type)

def load_model_from_redis(r, session_id):
    key = f"session:{session_id}:model"
    model = r.get(key)

    return model





