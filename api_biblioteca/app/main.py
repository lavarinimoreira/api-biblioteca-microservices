from fastapi import FastAPI
from app.routers import books, permissions, users, loans, policy_group, policy_group_permissions, auth, files
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",  # URL do front-end
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/healthy')
def health_check():
    return{'status': 'Healthy'}

app.include_router(files.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(policy_group.router)
app.include_router(permissions.router)
app.include_router(policy_group_permissions.router)

# app.mount("/images", StaticFiles(directory="images"), name="images")