import base64
import json

def encode(v1, v2, v3):
    data = {
        "value1": v1,
        "value2": v2,
        "value3": v3
    }

    json_data = json.dumps(data)
    encoded = base64.b64encode(json_data.encode()).decode()
    return encoded
