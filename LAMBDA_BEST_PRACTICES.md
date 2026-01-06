# AWS Lambda Best Practices Implementation

This document outlines the AWS Lambda best practices applied to this FastAPI serverless application, aligned with the latest AWS recommendations for 2024-2026.

## Summary of Changes

### 1. **Python 3.13 Runtime** ✨ NEW
- **Updated from:** Python 3.12
- **Updated to:** Python 3.13 (latest supported runtime)
- **Benefits:**
  - Latest security patches and bug fixes
  - Improved performance and startup times
  - Support until at least October 2029
  - Access to latest Python language features

### 2. **ARM64 Architecture** 💰 Cost Optimization
- **Added:** `Architectures: [arm64]` to SAM template
- **Benefits:**
  - **Up to 20% cost savings** compared to x86_64
  - Better price-to-performance ratio
  - Improved cold start times
  - Lower carbon footprint

### 3. **Resource Initialization Outside Handler** ⚡ Performance
- **Implementation:** Moved AWS SDK clients (boto3) outside the handler function
- **Code Pattern:**
  ```python
  # Initialize outside handler for reuse across invocations
  dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION"))
  s3 = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION"))
  ```
- **Benefits:**
  - Leverages Lambda execution environment reuse
  - Reduces cold start time
  - Minimizes SDK initialization overhead
  - Connection pooling benefits

### 4. **AWS Powertools for Lambda** 📊 Observability
- **Added:** `aws-lambda-powertools[all]` to requirements.txt
- **Implementation:** Structured logging with correlation IDs
- **Code Pattern:**
  ```python
  from aws_lambda_powertools import Logger
  logger = Logger(service="dynamodb-api")
  logger.info("Operation completed", extra={"item_id": id})
  ```
- **Benefits:**
  - Structured JSON logging for CloudWatch Logs Insights
  - Automatic request correlation
  - Built-in metrics and tracing support
  - Standardized logging format
  - Enhanced debugging capabilities

### 5. **Modern DynamoDB API** 🔄 Best Practices
- **Replaced:** Deprecated `AttributeUpdates` API
- **With:** Modern `UpdateExpression` API
- **Old Code:**
  ```python
  attrs = {k: {"Value": v, "Action": "PUT"} for k, v in update.items()}
  table.update_item(Key={"id": item_id}, AttributeUpdates=attrs)
  ```
- **New Code:**
  ```python
  update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update.keys()])
  expression_attribute_names = {f"#{k}": k for k in update.keys()}
  expression_attribute_values = {f":{k}": v for k, v in update.items()}
  table.update_item(
      Key={"id": item_id},
      UpdateExpression=update_expression,
      ExpressionAttributeNames=expression_attribute_names,
      ExpressionAttributeValues=expression_attribute_values
  )
  ```
- **Benefits:**
  - Follows AWS best practices
  - More flexible and powerful
  - Better performance
  - Support for conditional updates

### 6. **Explicit Region Configuration** 🌍
- **Added:** Explicit `region_name` parameter to boto3 clients
- **Benefits:**
  - Reduces AWS SDK initialization time
  - Eliminates region discovery overhead
  - More predictable behavior
  - Better for cross-region deployments

### 7. **Enhanced Error Handling** 🛡️
- **Implementation:** Proper exception handling with specific error types
- **Features:**
  - Catches `ClientError` from botocore
  - Logs errors with context
  - Returns appropriate HTTP status codes
  - Differentiates between client and server errors

### 8. **Mangum Lifespan Optimization** 🚀
- **Changed:** `handler = Mangum(app, lifespan="off")`
- **Benefits:**
  - Optimized for Lambda's event-driven nature
  - Prevents unnecessary lifecycle overhead
  - Better cold start performance

### 9. **Environment Variables for Configuration** ⚙️
- **Added to SAM template:**
  ```yaml
  POWERTOOLS_SERVICE_NAME: fastapi-lambda
  LOG_LEVEL: INFO
  ```
- **Benefits:**
  - Centralized configuration
  - Easy environment-specific settings
  - No code changes for configuration updates

## Architecture Benefits

### Cost Optimization
- **ARM64 architecture:** ~20% cost reduction
- **Efficient resource initialization:** Reduced execution time
- **Connection reuse:** Fewer cold starts

### Performance Improvements
- **Python 3.13:** Latest runtime optimizations
- **Client initialization outside handler:** Faster warm starts
- **ARM64:** Better price-to-performance ratio

### Operational Excellence
- **Structured logging:** Enhanced troubleshooting with CloudWatch Logs Insights
- **AWS Powertools:** Industry-standard observability
- **Proper error handling:** Better debugging and monitoring

### Security
- **Latest runtime:** Current security patches
- **Bucket owner verification:** Enhanced S3 security (already implemented)
- **Explicit error messages:** No sensitive data leakage

## Deployment Considerations

### Testing
All existing tests pass without modifications, confirming backward compatibility:
```bash
pytest tests/ -v
# 11 passed
```

### Migration Path
1. Deploy to a staging environment first
2. Monitor CloudWatch Logs for structured logging output
3. Verify ARM64 compatibility with all dependencies
4. Test cold and warm start performance
5. Gradually roll out to production

### Monitoring
With AWS Powertools, you can now:
- Query logs with CloudWatch Logs Insights
- Track performance metrics
- Implement distributed tracing with X-Ray
- Set up custom alarms based on structured log data

## Additional Best Practices to Consider

### Future Enhancements (Optional)
1. **Provisioned Concurrency**: For latency-critical endpoints
2. **Lambda Layers**: Share common dependencies across functions
3. **SnapStart**: When available for Python (currently Java only)
4. **Response Streaming**: For large payloads (>6MB)
5. **Idempotency**: Use Powertools idempotency utilities for event-driven functions
6. **Input Validation**: Replace dict with Pydantic models for type safety

### Continuous Improvement
- Monitor AWS Lambda announcements for new features
- Regularly update dependencies
- Review CloudWatch metrics and logs
- Optimize memory allocation based on actual usage
- Consider AWS Compute Optimizer recommendations

## References
- [AWS Lambda Python 3.13 Runtime](https://aws.amazon.com/blogs/compute/python-3-13-runtime-now-available-in-aws-lambda/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [AWS Powertools for Python](https://docs.aws.amazon.com/powertools/python/latest/)
- [ARM64 Architecture Benefits](https://aws.amazon.com/blogs/compute/migrating-aws-lambda-functions-to-arm-based-aws-graviton2-processors/)
- [DynamoDB UpdateExpression](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html)

---

**Last Updated:** January 2026  
**Compatible Runtime:** Python 3.13 on ARM64  
**Status:** Production Ready ✅
