import logging
from fastapi import FastAPI

from db.routines import prepare_database, shutdown_database
from routers import wallets, transactions


app = FastAPI()


@app.on_event('startup')
async def initialize():
    await prepare_database()

@app.on_event('shutdown')
async def shutdown():
    await shutdown_database()

app.include_router(wallets.router)
app.include_router(transactions.router)
