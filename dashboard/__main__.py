"""Allow running the dashboard with: python -m dashboard"""
from .app import app

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("DASHBOARD_PORT", 8050))
    uvicorn.run(app, host="0.0.0.0", port=port)
