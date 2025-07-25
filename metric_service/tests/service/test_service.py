import pytest
import json
import sys
import os
import re
from metric_service.api.service import app, latest_data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        latest_data.clear()
        yield client


def test_main_page(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'<html' in res.data or b'<!DOCTYPE html>' in res.data


def test_receive_and_show(client):
    test_payload = {
        "CPU": 4,
        "Virtual Memory": 8000000000,
        "Used RAM": 66.7,
        "Memory Left": 35.2
    }
    res = client.post('/receive', json=test_payload)
    assert res.status_code == 200
    assert res.get_json() == test_payload

    res = client.get('/show')
    assert res.status_code == 200
    data = res.get_json()
    assert "Data" in data
    assert test_payload in data["Data"]


def test_show_no_data(client):
    res = client.get('/show')
    assert res.status_code == 200
    data = res.get_json()
    assert "message" in data
    assert data["message"] == "No data received yet"


def test_metrics_initial_state(client):
    res = client.get('/metrics')
    assert res.status_code == 200
    assert res.headers['Content-Type'] == 'text/plain; version=0.0.4; charset=utf-8'
    content = res.data.decode()

    assert 'system_cpu_usage 0.0' in content
    assert 'system_virtual_memory 0.0' in content
    assert 'system_used_ram 0.0' in content
    assert 'system_memory_left 0.0' in content


def test_metrics_after_data_post(client):
    test_payload = {
        "CPU": 4,
        "Virtual Memory": 8000000000,
        "Used RAM": 66.7,
        "Memory Left": 35.2
    }

    client.post('/receive', json=test_payload)
    res = client.get('/metrics')
    content = res.data.decode()

    assert f'system_cpu_usage {float(test_payload["CPU"])}' in content
    assert re.search(r'system_virtual_memory\s+(8(?:\.0+)?e\+09|8000000000(?:\.0+)?)', content)
    assert f'system_used_ram {test_payload["Used RAM"]}' in content
    assert f'system_memory_left {test_payload["Memory Left"]}' in content
