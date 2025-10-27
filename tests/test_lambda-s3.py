# type: ignore
"""Tests for Lambda S3 function using mocked AWS services."""
import os
import sys
import boto3
import importlib.util
from fastapi.testclient import TestClient
from moto import mock_aws

# Set AWS region and mock credentials before importing app
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['BUCKET_NAME'] = 'test-bucket'


def _load_s3_app():
    """Load the S3 app module dynamically to avoid import conflicts."""
    app_path = os.path.join(os.path.dirname(__file__), '..', 'lambda-s3', 'app.py')
    spec = importlib.util.spec_from_file_location("s3_app", app_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module.app


@mock_aws
def test_get_file_success():
    """Test retrieving a file from S3 via the FastAPI endpoint."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload a test file
    test_content = b'Hello, this is a test file!'
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='test-file.txt',
        Body=test_content
    )
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET /files/{file_key} endpoint
    resp = client.get('/files/test-file.txt')
    assert resp.status_code == 200
    assert resp.content == test_content
    assert resp.headers['content-type'] == 'text/plain; charset=utf-8'


@mock_aws
def test_get_file_not_found():
    """Test retrieving a non-existent file returns 404."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET for non-existent file
    resp = client.get('/files/nonexistent-file.txt')
    assert resp.status_code == 404
    assert 'detail' in resp.json()
    assert resp.json()['detail'] == 'File not found'


@mock_aws
def test_get_file_with_path():
    """Test retrieving a file with a path prefix."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload a test file with path
    test_content = b'File in subdirectory'
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='folder/subfolder/document.txt',
        Body=test_content
    )
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET with path
    resp = client.get('/files/folder/subfolder/document.txt')
    assert resp.status_code == 200
    assert resp.content == test_content


@mock_aws
def test_get_file_binary_content():
    """Test retrieving binary file content."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload a binary file (simulated image data)
    binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='image.png',
        Body=binary_content,
        ContentType='image/png'
    )
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET for binary file
    resp = client.get('/files/image.png')
    assert resp.status_code == 200
    assert resp.content == binary_content


@mock_aws
def test_get_file_with_bucket_owner():
    """Test retrieving a file with bucket owner verification."""
    # Set environment variable for bucket owner
    os.environ['BUCKET_OWNER'] = '123456789012'
    
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload a test file
    test_content = b'Secure file content'
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='secure-file.txt',
        Body=test_content
    )
    
    # Import app after mock is set up (need to reload to pick up BUCKET_OWNER)
    import importlib
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET with bucket owner parameter
    resp = client.get('/files/secure-file.txt')
    assert resp.status_code == 200
    assert resp.content == test_content
    
    # Clean up
    del os.environ['BUCKET_OWNER']


@mock_aws
def test_get_empty_file():
    """Test retrieving an empty file."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload an empty file
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='empty.txt',
        Body=b''
    )
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET for empty file
    resp = client.get('/files/empty.txt')
    assert resp.status_code == 200
    assert resp.content == b''


@mock_aws
def test_get_large_file():
    """Test retrieving a larger file."""
    # Set up in-memory S3 bucket
    s3_client = boto3.client('s3')  # type: ignore[misc]
    s3_client.create_bucket(Bucket='test-bucket')  # type: ignore[attr-defined]
    
    # Upload a larger test file (1MB)
    large_content = b'A' * (1024 * 1024)  # 1MB of 'A's
    s3_client.put_object(  # type: ignore[attr-defined]
        Bucket='test-bucket',
        Key='large-file.bin',
        Body=large_content
    )
    
    # Import app after mock is set up
    app = _load_s3_app()
    
    client = TestClient(app)
    
    # Test GET for large file
    resp = client.get('/files/large-file.bin')
    assert resp.status_code == 200
    assert len(resp.content) == 1024 * 1024
    assert resp.content == large_content

