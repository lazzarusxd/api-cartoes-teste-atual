import pika
from connection import get_channel


def send_message(queue_name: str, message: str):
    connection, channel = get_channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"Mensagem enviada para a fila '{queue_name}': {message}")
    connection.close()
