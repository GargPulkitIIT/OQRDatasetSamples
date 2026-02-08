import base64
import json

def decode(encoded_data):
    try:
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_json = decoded_bytes.decode()
        data = json.loads(decoded_json)
        return data["value1"], data["value2"], data["value3"]
    except Exception:
        return None, None, None
