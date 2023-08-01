import pytest
from flask import session
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_home_route_authenticated(client):
    # Simulate an authenticated user
    with client.session_transaction() as sess:
        sess['username'] = 'test_user'
        sess['id'] = 1

    # Make a GET request to the home route
    response = client.get('/')

    assert response.status_code == 200
    assert b'Welcome, test_user' in response.data


def test_home_route_unauthenticated(client):
    # Simulate an unauthenticated user
    with client.session_transaction() as sess:
        sess.clear()

    # Make a GET request to the home route
    response = client.get('/')

    assert response.status_code == 302
    assert b'Redirecting' in response.data


def test_register_route(client):
    # Make a GET request to the register route
    response = client.get('/register')

    assert response.status_code == 200
    assert b'register' in response.data

def test_login_route(client):
    # Make a GET request to the login route
    response = client.get('/login')

    assert response.status_code == 200
    assert b'Login' in response.data


def test_login_route_post(client):
    # Make a POST request to the login route with valid data
    response = client.post('/login', data={
        'username': 'test',
        'password': 'test'
    })

    assert response.status_code == 302
    assert response.location == '/'


def test_logout_route(client):
    # Simulate an authenticated user
    with client.session_transaction() as sess:
        sess['username'] = 'test_user'
        sess['id'] = 1

    # Make a GET request to the logout route
    response = client.get('/logout')

    assert response.status_code == 302
    assert response.location == '/login'
    assert session.get('username') is None
    assert session.get('id') is None
def test_home_route_authenticated(client):
    # Simulate an authenticated user
    with client.session_transaction() as sess:
        sess['username'] = 'test'
        sess['id'] = 1

    # Make a POST request to the home route
    response = client.post('/', data={
        'start_location': 'Start Location',
        'end_location': 'End Location',
    })
    
    assert response.status_code == 302

def test_generate_ticket_route_unauthenticated(client):
    # Simulate an unauthenticated user
    with client.session_transaction() as sess:
        sess.clear()

    # Make a GET request to the generate_ticket route
    response = client.get('/generate_ticket')

    assert response.status_code == 302
    assert response.location == '/login'
    # Add more assertions based on the behavior of the generate_ticket route with an unauthenticated user

def test_process_qr_code_route(client):
    # Make a POST request to the process_qr_code route
    response = client.post('/process_qr_code', data={
        'qr_code_data': 'QR Code Data',
    })

    assert response.status_code == 200

import time
import os
from ticket import Ticket, generate_qr_code

@pytest.fixture
def ticket_data():
    return {
        'id': 'random_hash',
        'creation_time': time.time(),
        'start_location': 'Start',
        'destination': 'Destination',
        'qr_code_file': 'static/tickets/random_hash.png'
    }

def test_ticket_is_valid(ticket_data):
    ticket = Ticket(**ticket_data)

    # Ticket should be valid immediately after creation
    assert ticket.is_valid()

def test_ticket_invalid_after_validity_period(ticket_data):
    ticket_data['creation_time'] = time.time() - 3700  # Set creation time to 1 hour and 1 second ago
    ticket = Ticket(**ticket_data)

    # Ticket should not be valid after 1 hour has passed
    assert not ticket.is_valid()

def test_valid_upto(ticket_data):
    ticket = Ticket(**ticket_data)

    # Ticket's validity should be 1 hour
    assert ticket.valid_upto() == 3600

def test_generate_qr_code(tmpdir):
    start_location = 'Start'
    destination = 'Destination'
    qr_code_file = tmpdir.join('test_qr_code.png').strpath

    ticket = generate_qr_code(start_location, destination, qr_code_file=qr_code_file)

    # Check if the QR code file was generated and exists
    assert os.path.exists(qr_code_file)

    # Check if the Ticket object was returned with correct attributes
    assert ticket.id
    assert ticket.creation_time
    assert ticket.start_location == start_location
    assert ticket.destination == destination
    assert ticket.qr_code_file == qr_code_file

def test_ticket_remove_qr_code(ticket_data, tmpdir):
    ticket_data['qr_code_file'] = tmpdir.join('test_qr_code.png').strpath
    ticket = Ticket(**ticket_data)

    # Create a dummy QR code file
    with open(ticket.qr_code_file, 'w') as file:
        file.write('Dummy QR code data')

    # Check if the dummy QR code file exists before removing
    assert os.path.exists(ticket.qr_code_file)

    # Remove the QR code file using the remove method
    ticket.remove()

    # Check if the QR code file was removed
    assert not os.path.exists(ticket.qr_code_file)
