from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from local_llm import UnitTestGenerator
from pydantic import BaseModel
import os
import logging
import uvicorn
import tempfile
import uuid
import time
import asyncio


class GenerateRequest(BaseModel):
    code: str
    model_name: str


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

# store tasks
# create async function to run task
# stop task usiing ?

unitTestGenerator = UnitTestGenerator()
tasks = {}


async def run_unit_test_task(task_id: str, code: str, model_name: str):
    # still confuse why set at the start or it will be set using different method ?
    cancel_event = tasks[task_id]["cancel_event"]
    try:
        logger.info(f"Running unit test task with ID: {task_id}")
        tasks[task_id]["status"] = "running"

        # add cancle event to this function
        result = await unitTestGenerator.generate_unit_tests(code, model_name, cancel_event=cancel_event)

        # cancel event set when task need to be stopped
        if cancel_event.is_set():
            tasks[task_id]["status"] = "stopped"
            logger.warning(f"[{task_id}] Task cancelled via asyncio.")
            return

        tasks[task_id]["result"] = result
        tasks[task_id]["status"] = "complete"
        logger.info(f"[{task_id}] Task completed.")

    # cancle
    except asyncio.CancelledError:
        tasks[task_id]["status"] = "stopped"
        logger.warning(f"[{task_id}] Task cancelled via asyncio.")
    # actual exception
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = str(e)
        logger.exception(f"[{task_id}] Task failed: {e}")


@app.get("/")
async def root():
    return {"message": "Welcome to UnitTest Generator API. You can generate unit tests for your code"}


@app.post("/generate/unit-test")
async def generate_unit_test(
    code: str = Form(...),
    model_name: str = Form(...)
):
    task_id = str(uuid.uuid4())
    # event for cancel task
    cancel_event = asyncio.Event()
    task = asyncio.create_task(run_unit_test_task(task_id, code, model_name))

    # add to tasks
    tasks[task_id] = {
        "status": "pending",
        "result": None,
        "task": task,
        "cancel_event": cancel_event
    }

    logger.info(f"Task with ID: {task_id} started.")
    return {"task_id": task_id, "status": "pending"}


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    # if tasks not found
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    # if task is complete return result
    # if task is not complete return current status
    if tasks[task_id]["status"] == "complete":
        return {
            "message": "Task is complete.",
            "task_id": task_id,
            "status": tasks[task_id]["status"],
            "result": tasks[task_id]["result"]
        }
    else:
        return {
            "message": "Task is not complete yet.",
            "task_id": task_id,
            "status": tasks[task_id]["status"]
        }


@app.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    if tasks[task_id]["status"] not in ["pending", "running"]:
        return {
            "message": "Task cannot be cancelled.",
            "task_id": task_id,
            "status": tasks[task_id]["status"]
        }

    tasks[task_id]["cancel_event"].set()
    logger.info(f"Task with ID: {task_id} cancelled.")
    return {
        "message": "Task cancelled.",
        "task_id": task_id,
        "status": tasks[task_id]["status"]
    }


@app.get("/models")
async def get_models():
    try:
        models = await unitTestGenerator.get_available_models()
        return {
            "message": "Available models.",
            "models": models
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get available models")


if __name__ == "__main__":
    print("Starting server...")
    logger.info("Server running on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True, log_level="info")
