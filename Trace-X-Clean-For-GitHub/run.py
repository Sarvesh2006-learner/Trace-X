from backend.app import app
from backend.models.auth_event import AuthEvent
app.run(host="127.0.0.1", port=5000, debug=True)
