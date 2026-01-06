# AWS FastAPI Serverless Architecture

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688.svg)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20API%20Gateway-orange.svg)](https://aws.amazon.com/)

A production-ready, serverless REST API built with FastAPI and deployed on AWS Lambda. This project demonstrates modern cloud architecture patterns using AWS SAM (Serverless Application Model) to create scalable, cost-effective microservices with DynamoDB and S3 integration.

## 🌟 Features

- **🚀 Serverless Architecture**: Zero server management with automatic scaling via AWS Lambda
- **⚡ High Performance**: FastAPI framework delivering exceptional speed and performance
- **🔄 RESTful APIs**: Clean, well-documented REST endpoints for DynamoDB and S3 operations
- **🛡️ Security First**: IAM roles with least-privilege access, encrypted S3 buckets, and secure API Gateway
- **📦 Infrastructure as Code**: Complete AWS SAM template for reproducible deployments
- **✅ Comprehensive Testing**: Full test coverage using moto for AWS service mocking
- **🌍 Multi-Environment Support**: Separate dev, staging, and production configurations
- **📊 Observability**: Built-in CloudWatch logging and X-Ray tracing support

## 🏗️ Architecture

This project implements a serverless microservices architecture:

```
┌─────────────────┐
│   API Gateway   │  ← HTTPS Entry Point
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Lambda │ │Lambda │
│DynamoDB│ │  S3   │
└───┬───┘ └──┬────┘
    │         │
┌───▼────┐ ┌─▼─────┐
│DynamoDB│ │  S3   │
│ Table  │ │Bucket │
└────────┘ └───────┘
```

### Components

- **API Gateway**: Managed REST API with CORS support and request/response transformation
- **Lambda Functions**: 
  - `DynamoDB Function`: Handles CRUD operations for items storage
  - `S3 Function`: Manages file retrieval from S3 buckets
- **DynamoDB**: NoSQL database for low-latency data storage
- **S3**: Object storage for files with server-side encryption
- **IAM Roles**: Scoped permissions for each Lambda function

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12** or higher
- **AWS CLI** configured with appropriate credentials
- **AWS SAM CLI** for local development and deployment
- **Docker** (for SAM local testing)

### Install AWS SAM CLI

```bash
# macOS
brew tap aws/tap
brew install aws-sam-cli

# Windows (using Chocolatey)
choco install aws-sam-cli

# Linux
pip install aws-sam-cli
```

### Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ParthibanRajasekaran/aws-fastapi.git
cd aws-fastapi
```

### 2. Install Dependencies

```bash
# Install dependencies for DynamoDB Lambda
cd lambda-dynamo
pip install -r requirements.txt
cd ..

# Install dependencies for S3 Lambda
cd lambda-s3
pip install -r requirements.txt
cd ..
```

### 3. Deploy to AWS

Deploy to your AWS account using SAM CLI:

```bash
# Build the application
sam build

# Deploy with guided prompts (first time)
sam deploy --guided

# Or deploy with saved configuration
sam deploy
```

During guided deployment, you'll be prompted for:
- **Stack Name**: Name for your CloudFormation stack (e.g., `aws-fastapi-dev`)
- **Region**: AWS region for deployment (e.g., `us-east-1`)
- **Environment**: Choose from `dev`, `staging`, or `prod`
- **Confirm changes**: Review the changeset before deployment

### 4. Get Your API Endpoint

After successful deployment, the API URL will be displayed in the outputs:

```bash
# Get the API endpoint
aws cloudformation describe-stacks \
  --stack-name aws-fastapi-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

## 📖 API Documentation

### DynamoDB API Endpoints

#### Create Item
```bash
POST /items
Content-Type: application/json

{
  "id": "item-123",
  "value": "Sample data",
  "description": "Additional attributes"
}
```

**Response:**
```json
{
  "message": "Item item-123 created."
}
```

#### Update Item
```bash
PUT /items/{item_id}
Content-Type: application/json

{
  "value": "Updated data",
  "description": "Modified attributes"
}
```

**Response:**
```json
{
  "message": "Item item-123 updated."
}
```

#### Get Item
```bash
GET /items/{item_id}
```

**Response:**
```json
{
  "id": "item-123",
  "value": "Sample data",
  "description": "Additional attributes"
}
```

### S3 API Endpoints

#### Get File
```bash
GET /files/{file_key}
```

**Example:**
```bash
GET /files/documents/report.pdf
```

**Response:** File content with appropriate Content-Type header

## 🛠️ Local Development

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov moto boto3-stubs[dynamodb,s3]

# Run all tests
pytest

# Run with coverage
pytest --cov=lambda-dynamo --cov=lambda-s3 --cov-report=html

# Run specific test file
pytest tests/test_lambda-dynamo.py
```

### Local API Testing with SAM

Start the API locally using SAM:

```bash
# Build the application
sam build

# Start local API Gateway
sam local start-api

# Your API will be available at http://127.0.0.1:3000
```

Test the local endpoints:

```bash
# Create an item
curl -X POST http://127.0.0.1:3000/items \
  -H "Content-Type: application/json" \
  -d '{"id": "test-1", "value": "Hello Local"}'

# Get an item
curl http://127.0.0.1:3000/items/test-1
```

### Local Development with Uvicorn

For rapid development, you can run the FastAPI apps directly:

```bash
# Run DynamoDB API locally
cd lambda-dynamo
export TABLE_NAME=ItemsTable
uvicorn app:app --reload --port 8000

# Run S3 API locally (in another terminal)
cd lambda-s3
export BUCKET_NAME=my-local-bucket
uvicorn app:app --reload --port 8001
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📁 Project Structure

```
aws-fastapi/
├── lambda-dynamo/           # DynamoDB Lambda function
│   ├── app.py              # FastAPI application for DynamoDB operations
│   └── requirements.txt    # Python dependencies
├── lambda-s3/              # S3 Lambda function
│   ├── app.py              # FastAPI application for S3 operations
│   └── requirements.txt    # Python dependencies
├── tests/                  # Test suite
│   ├── test_lambda-dynamo.py  # DynamoDB function tests
│   └── test_lambda-s3.py      # S3 function tests
├── template.yaml           # AWS SAM template (Infrastructure as Code)
├── pyrightconfig.json      # Python type checking configuration
├── LICENSE                 # Apache 2.0 license
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

Each Lambda function uses environment variables for configuration:

**DynamoDB Function:**
- `TABLE_NAME`: DynamoDB table name (set by SAM template)
- `AWS_DEFAULT_REGION`: AWS region (automatically set)

**S3 Function:**
- `BUCKET_NAME`: S3 bucket name (set by SAM template)
- `BUCKET_OWNER`: (Optional) AWS Account ID for bucket ownership verification

### SAM Template Parameters

Customize deployment via `template.yaml` parameters:

- **Environment**: Deployment environment (`dev`, `staging`, `prod`)
- **BucketOwner**: AWS Account ID for S3 bucket ownership verification

### Resource Configuration

Key settings in `template.yaml`:
- **Timeout**: 30 seconds (adjustable for longer operations)
- **Memory**: 256 MB (tune based on workload)
- **Runtime**: Python 3.12
- **Billing Mode**: DynamoDB PAY_PER_REQUEST (scales automatically)

## 🔒 Security

This project implements AWS security best practices:

- ✅ **Least Privilege IAM**: Lambda functions have minimal required permissions
- ✅ **Encryption at Rest**: S3 buckets use AES-256 encryption
- ✅ **Private S3 Buckets**: Public access blocked by default
- ✅ **API Gateway CORS**: Configurable cross-origin resource sharing
- ✅ **VPC Support**: Can be extended to run in VPC for enhanced isolation
- ✅ **Environment Isolation**: Separate resources per environment
- ✅ **CloudWatch Logging**: All function invocations are logged
- ✅ **X-Ray Tracing**: Distributed tracing enabled for debugging

### Bucket Ownership Verification

For enhanced security, S3 operations can verify bucket ownership:

```bash
sam deploy --parameter-overrides BucketOwner=123456789012
```

## 📊 Monitoring and Observability

### CloudWatch Logs

View Lambda function logs:

```bash
# View DynamoDB function logs
sam logs -n DynamoDBFunction --stack-name aws-fastapi-dev --tail

# View S3 function logs
sam logs -n S3Function --stack-name aws-fastapi-dev --tail
```

### CloudWatch Metrics

Monitor key metrics in CloudWatch:
- Invocation count
- Error rate
- Duration
- Throttles
- Concurrent executions

### X-Ray Tracing

X-Ray tracing is enabled by default on the API Gateway. View traces in the AWS X-Ray console to analyze:
- Request latency
- Service map
- Downstream calls to DynamoDB/S3

## 🚢 Deployment

### CI/CD Integration

This project is ready for CI/CD integration with services like:
- **AWS CodePipeline**: Native AWS CI/CD
- **GitHub Actions**: Automated deployments on push
- **GitLab CI**: Pipeline-based deployments
- **Jenkins**: Traditional CI/CD integration

Example GitHub Actions workflow:

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: aws-actions/setup-sam@v2
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - run: sam build
      - run: sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

### Multi-Region Deployment

Deploy to multiple regions for high availability:

```bash
# Deploy to us-east-1
sam deploy --region us-east-1 --stack-name aws-fastapi-prod-use1

# Deploy to eu-west-1
sam deploy --region eu-west-1 --stack-name aws-fastapi-prod-euw1
```

## 🧪 Testing Strategy

This project includes comprehensive tests:

- **Unit Tests**: Test individual functions and logic
- **Integration Tests**: Test API endpoints with mocked AWS services
- **Mocked AWS Services**: Use `moto` library for local AWS simulation
- **Test Coverage**: Aim for >90% code coverage

Run tests before deployment:

```bash
pytest --cov --cov-report=term-missing
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Use type hints for better code clarity

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Mangum](https://github.com/jordaneremieff/mangum) - AWS Lambda adapter for ASGI applications
- [AWS SAM](https://aws.amazon.com/serverless/sam/) - Serverless Application Model
- [Moto](https://github.com/getmoto/moto) - AWS service mocking for testing

## 📞 Support

For questions, issues, or suggestions:

- 🐛 **Issues**: [GitHub Issues](https://github.com/ParthibanRajasekaran/aws-fastapi/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ParthibanRajasekaran/aws-fastapi/discussions)

## 🗺️ Roadmap

Future enhancements planned:

- [ ] GraphQL API support
- [ ] WebSocket support for real-time updates
- [ ] Cognito authentication integration
- [ ] API key management
- [ ] Rate limiting and throttling
- [ ] Request validation with Pydantic models
- [ ] OpenAPI schema validation
- [ ] Performance benchmarking suite
- [ ] Blue-green deployment support
- [ ] CloudFormation cross-stack references

---

**Built with ❤️ using FastAPI, AWS Lambda, and modern serverless architecture patterns**
