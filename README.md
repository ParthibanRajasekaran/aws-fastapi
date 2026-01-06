# AWS FastAPI Lambda Functions

A serverless FastAPI application deployed on AWS Lambda with best practices for 2024-2026. This project demonstrates how to build production-ready serverless APIs using FastAPI, AWS Lambda, DynamoDB, and S3.

## 🚀 Features

- **FastAPI Framework**: Modern, fast Python web framework
- **AWS Lambda**: Serverless compute with auto-scaling
- **DynamoDB Integration**: NoSQL database operations (CRUD)
- **S3 Integration**: File storage and retrieval
- **ARM64 Architecture**: 20% cost savings with Graviton2 processors
- **Python 3.13**: Latest Lambda runtime
- **AWS Powertools**: Structured logging and observability
- **Infrastructure as Code**: AWS SAM template for deployment

## 📋 Architecture

```
┌─────────────────┐
│  API Gateway    │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼────┐  ┌──▼──────┐
│ Lambda │  │ Lambda  │
│DynamoDB│  │   S3    │
│Function│  │Function │
└───┬────┘  └──┬──────┘
    │          │
┌───▼────┐  ┌──▼──┐
│DynamoDB│  │ S3  │
│ Table  │  │Bucket│
└────────┘  └─────┘
```

## 🏗️ Project Structure

```
.
├── lambda-dynamo/          # DynamoDB Lambda function
│   ├── app.py             # FastAPI app with DynamoDB operations
│   └── requirements.txt   # Python dependencies
├── lambda-s3/             # S3 Lambda function
│   ├── app.py             # FastAPI app with S3 operations
│   └── requirements.txt   # Python dependencies
├── tests/                 # Unit tests
│   ├── test_lambda-dynamo.py
│   └── test_lambda-s3.py
├── template.yaml          # AWS SAM template
├── LAMBDA_BEST_PRACTICES.md  # Detailed best practices documentation
└── README.md              # This file
```

## 🛠️ Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.13 or higher
- Docker (for local testing)

## 🚦 Getting Started

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ParthibanRajasekaran/aws-fastapi.git
   cd aws-fastapi
   ```

2. **Install dependencies:**
   ```bash
   # For DynamoDB function
   cd lambda-dynamo
   pip install -r requirements.txt
   cd ..

   # For S3 function
   cd lambda-s3
   pip install -r requirements.txt
   cd ..
   ```

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

### Deployment

1. **Build the application:**
   ```bash
   sam build
   ```

2. **Deploy to AWS:**
   ```bash
   sam deploy --guided
   ```

   Follow the prompts to configure:
   - Stack name
   - AWS Region
   - Environment (dev/staging/prod)
   - Bucket owner account ID (optional)

3. **Get the API endpoint:**
   ```bash
   sam list stack-outputs
   ```

## 📡 API Endpoints

### DynamoDB Operations

- **POST /items** - Create a new item
  ```bash
  curl -X POST https://your-api-url/dev/items \
    -H "Content-Type: application/json" \
    -d '{"id": "item1", "value": "Hello World"}'
  ```

- **GET /items/{item_id}** - Get an item by ID
  ```bash
  curl https://your-api-url/dev/items/item1
  ```

- **PUT /items/{item_id}** - Update an item
  ```bash
  curl -X PUT https://your-api-url/dev/items/item1 \
    -H "Content-Type: application/json" \
    -d '{"value": "Updated Value"}'
  ```

### S3 Operations

- **GET /files/{file_key}** - Retrieve a file from S3
  ```bash
  curl https://your-api-url/dev/files/path/to/file.txt
  ```

## 🔬 Testing

The project includes comprehensive unit tests using pytest and moto for AWS service mocking:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_lambda-dynamo.py -v

# Run with coverage
pytest tests/ --cov=lambda-dynamo --cov=lambda-s3
```

## 🎯 Best Practices Implemented

This project follows AWS Lambda best practices for 2024-2026:

- ✅ **Python 3.13 Runtime** - Latest supported version
- ✅ **ARM64 Architecture** - 20% cost savings
- ✅ **Resource Initialization Outside Handler** - Better performance
- ✅ **AWS Powertools** - Structured logging and observability
- ✅ **Modern DynamoDB APIs** - UpdateExpression instead of deprecated AttributeUpdates
- ✅ **Explicit Region Configuration** - Reduced initialization time
- ✅ **Enhanced Error Handling** - Proper exception management
- ✅ **Environment-Based Configuration** - No hardcoded values

For detailed documentation, see [LAMBDA_BEST_PRACTICES.md](./LAMBDA_BEST_PRACTICES.md).

## 📊 Monitoring

With AWS Powertools integration, you can:

1. **CloudWatch Logs Insights** - Query structured logs:
   ```
   fields @timestamp, message, item_id, error
   | filter service = "dynamodb-api"
   | sort @timestamp desc
   ```

2. **X-Ray Tracing** - Enable in template.yaml for distributed tracing

3. **Custom Metrics** - Use Powertools metrics for business KPIs

## 🔐 Security

- S3 bucket encryption enabled (AES256)
- Public access blocked on S3 buckets
- IAM roles with least privilege access
- Bucket owner verification support
- API Gateway with CORS configuration

## 💰 Cost Optimization

- ARM64 architecture for 20% cost reduction
- Pay-per-request DynamoDB billing
- Efficient resource initialization for reduced execution time
- CloudWatch Logs with structured logging for better insights

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Lambda team for continuous runtime improvements
- FastAPI community for an excellent framework
- AWS Powertools for production-ready utilities

## 📚 Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Powertools for Python](https://docs.aws.amazon.com/powertools/python/latest/)

---

**Built with ❤️ using AWS Lambda, FastAPI, and Python 3.13**
