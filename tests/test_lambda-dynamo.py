# type: ignore
"""Tests for Lambda DynamoDB function using mocked AWS services."""
import os
import sys
import boto3
import importlib.util
from typing import TYPE_CHECKING
from fastapi.testclient import TestClient
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

# Set AWS region and mock credentials before importing app
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['TABLE_NAME'] = 'ItemsTable'


def _load_dynamo_app():
    """Load the DynamoDB app module dynamically to avoid import conflicts."""
    app_path = os.path.join(os.path.dirname(__file__), '..', 'lambda-dynamo', 'app.py')
    spec = importlib.util.spec_from_file_location("dynamo_app", app_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module.app


@mock_aws
def test_create_item():
    """Test creating an item in DynamoDB via the FastAPI endpoint."""
    # Set up in-memory DynamoDB table
    dynamodb = boto3.resource('dynamodb')  # type: ignore[misc]
    dynamodb.create_table(  # type: ignore[attr-defined]
        TableName='ItemsTable',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Import app after mock is set up
    app = _load_dynamo_app()
    
    client = TestClient(app)
    
    # Test POST /items endpoint
    item_data = {'id': 'test1', 'value': 'hello'}
    resp = client.post('/items', json=item_data)
    assert resp.status_code == 200
    assert 'message' in resp.json()
    
    # Verify the item was written to DynamoDB
    table = dynamodb.Table('ItemsTable')  # type: ignore[attr-defined]
    result = table.get_item(Key={'id': 'test1'})
    assert 'Item' in result
    assert result['Item']['value'] == 'hello'


@mock_aws
def test_update_item():
    """Test updating an item in DynamoDB via the FastAPI endpoint."""
    # Set up in-memory DynamoDB table
    dynamodb = boto3.resource('dynamodb')  # type: ignore[misc]
    dynamodb.create_table(  # type: ignore[attr-defined]
        TableName='ItemsTable',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Insert initial item
    table = dynamodb.Table('ItemsTable')  # type: ignore[attr-defined]
    table.put_item(Item={'id': 'test2', 'value': 'initial'})
    
    # Import app after mock is set up
    app = _load_dynamo_app()
    
    client = TestClient(app)
    
    # Test PUT /items/{item_id} endpoint
    update_data = {'value': 'updated'}
    resp = client.put('/items/test2', json=update_data)
    assert resp.status_code == 200
    assert 'message' in resp.json()
    
    # Verify the item was updated
    result = table.get_item(Key={'id': 'test2'})
    assert 'Item' in result
    assert result['Item']['value'] == 'updated'


@mock_aws
def test_get_item():
    """Test retrieving an item from DynamoDB via the FastAPI endpoint."""
    # Set up in-memory DynamoDB table
    dynamodb = boto3.resource('dynamodb')  # type: ignore[misc]
    dynamodb.create_table(  # type: ignore[attr-defined]
        TableName='ItemsTable',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Insert test item
    table = dynamodb.Table('ItemsTable')  # type: ignore[attr-defined]
    table.put_item(Item={'id': 'test3', 'value': 'retrieve_me'})
    
    # Import app after mock is set up
    app = _load_dynamo_app()
    
    client = TestClient(app)
    
    # Test GET /items/{item_id} endpoint
    resp = client.get('/items/test3')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == 'test3'
    assert data['value'] == 'retrieve_me'


@mock_aws
def test_get_item_not_found():
    """Test retrieving a non-existent item returns 404."""
    # Set up in-memory DynamoDB table
    dynamodb = boto3.resource('dynamodb')  # type: ignore[misc]
    dynamodb.create_table(  # type: ignore[attr-defined]
        TableName='ItemsTable',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Import app after mock is set up
    app = _load_dynamo_app()
    
    client = TestClient(app)
    
    # Test GET for non-existent item
    resp = client.get('/items/nonexistent')
    assert resp.status_code == 404
    assert 'detail' in resp.json()

