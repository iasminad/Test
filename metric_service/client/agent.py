import pika
import psutil
import json
import sys
from time import sleep
import threading


def send_metrics():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()
    channel.queue_declare(queue='metrics')

    for _ in range(10):
        metrics = {
            'CPU': psutil.cpu_count(),
            'Virtual Memory': psutil.virtual_memory().total,
            'Used RAM': round(psutil.virtual_memory().percent, 2),
            'Memory Left': round(psutil.virtual_memory().available * 100 /
                                 psutil.virtual_memory().total, 2)
        }
        metrics_json = json.dumps(metrics)

        channel.basic_publish(exchange='', routing_key='metrics',
                              body=metrics_json)
        print(" [x] Sent metrics!")
        print(metrics_json)

        sys.stdout.flush()
        sleep(3)

    connection.close()


def main():
    sleep(10)  # give RabbitMQ time to start
    sender_thread = threading.Thread(target=send_metrics)
    sender_thread.start()
    sender_thread.join()


if __name__ == '__main__':
    main()
