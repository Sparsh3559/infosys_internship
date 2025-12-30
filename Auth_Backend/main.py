from fastapi import FastAPI
from database import Base, engine
from routes.auth import router

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# APPLICATION SETUP
# --------------------------------------------------
app = FastAPI(
    title="AI Content Studio Backend",
    version="1.0.0"
)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
app.include_router(router)

# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}