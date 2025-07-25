import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os
from metric_service.server import collector


@patch('metric_service.server.collector.requests.post')
@patch('metric_service.server.collector.pika.BlockingConnection')
def test_consume_messages(mock_pika, mock_post):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_pika.return_value = mock_connection

    test_data = {
        "CPU": 4,
        "Virtual Memory": 8000000000,
        "Used RAM": 66.7,
        "Memory Left": 35.2
    }
    body = json.dumps(test_data).encode()

    callback_func = None

    def fake_basic_consume(queue, on_message_callback, auto_ack):
        nonlocal callback_func
        callback_func = on_message_callback

    mock_channel.basic_consume.side_effect = fake_basic_consume

    def fake_start_consuming():
        callback_func(mock_channel, MagicMock(delivery_tag=123), None, body)

    mock_channel.start_consuming.side_effect = fake_start_consuming

    collector.consume_messages()

    mock_channel.queue_declare.assert_called_once_with(queue='metrics')
    mock_channel.queue_purge.assert_called_once_with(queue='metrics')
    mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)

    mock_post.assert_called_once_with(
        "http://web:8000/receive",
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )

    mock_channel.basic_ack.assert_called_once_with(delivery_tag=123)
