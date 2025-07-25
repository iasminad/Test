import pika
import sys
import os
import json
from time import sleep
import requests
import threading


def consume_messages():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()

    channel.queue_declare(queue='metrics')
    channel.queue_purge(queue='metrics')
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(json.dumps(data, indent=2))

        try:
            res = requests.post(
                "http://web:8000/receive",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            print(f"Status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error posting to web service: {e}")

        sys.stdout.flush()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='metrics', on_message_callback=callback,
                          auto_ack=False)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


def main():
    sleep(10)

    thread = threading.Thread(target=consume_messages)
    thread.start()
    thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
