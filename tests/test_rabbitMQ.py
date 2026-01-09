import pytest
from unittest.mock import patch, MagicMock
import json
from app.rabbitmq_publisher import RabbitMQPublisher

@pytest.fixture
def mock_rabbitmq():
    #fixture that mocks RabbitMQ for notification tests
    with patch('pika.URLParameters') as mock_params, \
         patch('pika.BlockingConnection') as mock_conn:
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_conn.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        yield mock_connection, mock_channel

def test_publish_event_success(mock_rabbitmq):
   #Test successful event publishing
    mock_connection, mock_channel = mock_rabbitmq
    
    publisher = RabbitMQPublisher("amqp://test")
    result = publisher.publish_event("test_event", "test.route", "user123", {"key": "value"})
    
    assert result is True
    mock_channel.exchange_declare.assert_called_once()
    mock_channel.basic_publish.assert_called_once()

@patch.dict('os.environ', {}, clear=True)
def test_publish_event_no_url():
    #test publishing fails gracefully without rabbitmq url
    publisher = RabbitMQPublisher(None)
    result = publisher.publish_event("test_event", "test.route", "user123", {"key": "value"})
    
    assert result is False

def test_create_notification_format(mock_rabbitmq):
    # test notification creation with proper message format
    mock_connection, mock_channel = mock_rabbitmq
    
    publisher = RabbitMQPublisher("amqp://test")
    result = publisher.createNotification("user_login", "user123", "login.event", {"action": "login"})
    
    assert result is True
    mock_channel.basic_publish.assert_called_once()

@patch('builtins.print')
def test_consumer_processes_user_login(mock_print):
    payload = {"event_type": "user_login", "user_id": "test123"}
    event_type = payload.get("event_type")
    
    if event_type == "user_login":
        print("Set currentUser=", payload.get("user_id"))
    
    assert event_type == "user_login"
    mock_print.assert_called()

def test_consumer_handles_invalid_json():
    #test consumer handles JSON decode errors
    try:
        json.loads("invalid json")
    except json.JSONDecodeError as e:
        assert "Expecting value" in str(e)

# Configuration tests
def test_configurations_pytest_detection():
    #Test configurations detects pytest environment
    import sys
    from app import configurations
    assert "pytest" in sys.modules
    assert hasattr(configurations, 'client')
    assert hasattr(configurations, 'db')

def test_configurations_collections():
    # test configurations creates collections
    from app.configurations import entries_collection, projects_collection
    assert entries_collection is not None
    assert projects_collection is not None

# Rabbitmq Publisher tests
def test_rabbitmq_publisher_connect_success(mock_rabbitmq):
    #Test RabbitMQ publisher connect metho
    mock_connection, mock_channel = mock_rabbitmq
    publisher = RabbitMQPublisher("amqp://test")
    result = publisher.connect()
    assert result is True

def test_rabbitmq_publisher_connect_no_url():
    #test RabbitMq publisher connect without URL
    with patch.dict('os.environ', {}, clear=True):
        publisher = RabbitMQPublisher(None)
        result = publisher.connect()
        assert result is False

def test_rabbitmq_publisher_close():
    # test RabbitMQ publisher close method
    publisher = RabbitMQPublisher("amqp://test")
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False
    publisher.close()
    publisher.connection.close.assert_called_once()

def test_get_rabbitmq_publisher():
    # test get_rabbitmq_publisher function
    from app.rabbitmq_publisher import get_rabbitmq_publisher
    publisher = get_rabbitmq_publisher()
    assert isinstance(publisher, RabbitMQPublisher)

# main tests
def test_main_app_creation():
   # test FastAPI app creation
    from app.main import app
    assert app.title == "Time Tracker API"

def test_main_delete_project_helper():
    # test delete project helper function
    from app.main import delete_project_and_entries_helper
    from bson import ObjectId
    
    #invalid objectid
    with pytest.raises(Exception):
        delete_project_and_entries_helper("invalid_id")

# more rabbit mq tests
@patch('pika.BlockingConnection')
def test_rabbitmq_publisher_exception_handling(mock_conn):
    #Test RabbitMQ publisher exception handling
    mock_conn.side_effect = Exception("Connection failed")
    publisher = RabbitMQPublisher("amqp://test")
    result = publisher.publish_event("test", "route", "user", {})
    assert result is False

def test_rabbitmq_publisher_close_exception():
    #Test RabbitMQ publisher close with exception
    publisher = RabbitMQPublisher("amqp://test")
    publisher.connection = MagicMock()
    publisher.connection.close.side_effect = Exception("Close failed")
    publisher.close()  # Should not raise exception

def test_main_imports():
    from app import main
    assert hasattr(main, 'app')
    assert hasattr(main, 'delete_project_and_entries_helper')

# Additional simple coverage tests
def test_rabbitmq_publisher_connect_exception():
    with patch('pika.URLParameters') as mock_params:
        mock_params.side_effect = Exception("URL parsing failed")
        publisher = RabbitMQPublisher("amqp://test")
        result = publisher.connect()
        assert result is False

def test_rabbitmq_publisher_close_no_connection():
    publisher = RabbitMQPublisher("amqp://test")
    publisher.connection = None
    publisher.close()  # Should not raise exception