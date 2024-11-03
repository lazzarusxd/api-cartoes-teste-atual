from dotenv import load_dotenv
from os import environ
import pika

load_dotenv()

RABBITMQ_HOST = environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = int(environ.get("RABBITMQ_PORT"))


def get_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )


def get_channel():
    connection = get_connection()
    channel = connection.channel()
    return connection, channel
