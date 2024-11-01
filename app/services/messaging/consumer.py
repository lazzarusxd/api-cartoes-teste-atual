from connection import get_channel


def start_consumer(queue_name: str, callback_function):
    connection, channel = get_channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback_function,
        auto_ack=True
    )

    print(f"Consumindo mensagens da fila '{queue_name}'...")
    channel.start_consuming()


def callback_function(ch, method, properties, body):
    print(f"Mensagem recebida: {body.decode()}")
