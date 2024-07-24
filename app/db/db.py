import motor.motor_asyncio
import os
from beanie import init_beanie

from ..conf import DATABASE_URL
from ..model import LoggingModel
from ..model.user import Token, UserDocument, EmailConfigDocument
from ..model.job_service import JobPost, Resume


client = None


async def init_db():
    print("Initializing database")
    global client
    client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    await init_beanie(
        database=client.jobportal,
        document_models=[
            UserDocument,
            Token,
            LoggingModel,
            EmailConfigDocument,
            JobPost,
            Resume
        ],
    )

if not os.path.exists("resumes"):
    os.makedirs("resumes")

async def stop_db():
    print("Stopping database...")
    global client
    if client:
        client.close()
