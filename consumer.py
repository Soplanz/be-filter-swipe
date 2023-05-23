import pika
import json

import requests

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
channel = connection.channel()
channel.queue_declare(queue='notifications')

def callback(ch, method, properties, body):
    data = json.loads(body)
    print({data['message']})

channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()