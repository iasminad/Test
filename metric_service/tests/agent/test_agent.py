import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from metric_service.client.agent import send_metrics


class TestSendMetrics(unittest.TestCase):

    @patch('metric_service.client.agent.psutil')
    @patch('metric_service.client.agent.pika.BlockingConnection')
    @patch('metric_service.client.agent.sleep', return_value=None)
    def test_send_metrics_sends_correct_data(self, mock_sleep,
                mock_pika, mock_psutil):
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=8000000,
            percent=50.0,
            available=4000000
        )

        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.return_value = mock_connection

        send_metrics()

        mock_channel.queue_declare.assert_called_with(queue='metrics')

        self.assertEqual(mock_channel.basic_publish.call_count, 10)

        args, kwargs = mock_channel.basic_publish.call_args
        message_body = kwargs['body']
        metrics = json.loads(message_body)

        self.assertEqual(metrics['CPU'], 4)
        self.assertEqual(metrics['Virtual Memory'], 8000000)
        self.assertEqual(metrics['Used RAM'], 50.0)
        self.assertAlmostEqual(metrics['Memory Left'], 50.0)

        mock_connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
