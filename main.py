from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uvicorn
import tempfile
import uuid
import time
import asyncio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UnitTest Generator",)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to UnitTest Generator API. You can generate unit tests for your code"}


@app.post("/generate/unit-test")
async def generate_unit_test():
    return {"message": "This is the main endpoint for generating unit tests."}


@app.post("/status/{task_id}")
async def get_status(task_id: str):
    return {"message": f"This endpoint will return the status of the task with ID: {task_id}"}


@app.get("/models")
async def get_models():
    return {"message": "This endpoint will return the available models for unit test generation."}