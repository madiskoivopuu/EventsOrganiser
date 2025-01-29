import os, dotenv
dotenv.load_dotenv() # only for local testing, the docker container will already have environment variables set for it

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_VIRTUALHOST = os.getenv("RABBITMQ_VIRTUALHOST")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

LLM_PATH = os.getenv("LLM_PATH")