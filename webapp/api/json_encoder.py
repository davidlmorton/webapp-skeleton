from datetime import date, datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    "This is needed to convert datetime objects in JSON responses"
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
