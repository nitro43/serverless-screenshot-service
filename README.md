# Serverless AWS Python Screenshot Service

This will setup a screenshot api which will take a screenshot from a given url, and push it into an S3 bucket. 
This is all done with Lambda calls.

The screenshooting is done with Selenium using Chromium.
REST API with Flask and DynamoDB.

## Setup

```bash
npm install -g serverless
serverless plugin install -n serverless-wsgi
serverless plugin install -n serverless-python-requirements
bash fetch-binaries.sh
```

## run webserver locally
install requirements
```bash
serverless wsgi serve
```
## Deploy

```bash
serverless deploy
```

## Usage

### Create a screenshot

```bash
curl -X POST https://{endpoint_prefix}.execute-api.us-east-1.amazonaws.com/dev/make_screenshot --data '{ "url": "https://google.com" }'
```

result:
```bash
{"result":{"shot_url":"https://{bucket_name}.s3.amazonaws.com/{obj_id}","target_url":"https://google.com/"}}
```

### List all available screenshots

```bash
curl -X GET https://{endpoint_prefix}.execute-api.us-east-1.amazonaws.com/dev/screenshots
```
result:
```bash
{"result":[{"shot_url":"https://{bucket_name}.s3.amazonaws.com/fa4448c13e06e69ba9e814e8743c7e2e","target_url":"https://vk.com"},{"shot_url":"https://{bucket_name}.s3.amazonaws.com/e203e98e4c606735cf56db84a002fd22","target_url":"https://www.facebook.com/"}]}
```

### Get one screenshot.

```bash
curl -X POST https://{endpoint_prefix}.execute-api.eu-central-1.amazonaws.com/dev/screenshots -d "url=https://google.com"

```

result:
```bash
{"result":{"shot_url":"https://{bucket_name}.s3.amazonaws.com/{obj_id}","target_url":"https://google.com/"}}

```

## Scaling

### AWS Lambda

By default, AWS Lambda limits the total concurrent executions across all functions within a given region to 100. The default limit is a safety limit that protects you from costs due to potential runaway or recursive functions during initial development and testing. To increase this limit above the default, follow the steps in [To request a limit increase for concurrent executions](http://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html#increase-concurrent-executions-limit).

### DynamoDB

When you create a table, you specify how much provisioned throughput capacity you want to reserve for reads and writes. DynamoDB will reserve the necessary resources to meet your throughput needs while ensuring consistent, low-latency performance. You can change the provisioned throughput and increasing or decreasing capacity as needed.

This is can be done via settings in the `serverless.yml`.

```yaml
  ProvisionedThroughput:
    ReadCapacityUnits: 1
    WriteCapacityUnits: 1
```

In case you expect a lot of traffic fluctuation we recommend to checkout this guide on how to auto scale DynamoDB [https://aws.amazon.com/blogs/aws/auto-scale-dynamodb-with-dynamic-dynamodb/](https://aws.amazon.com/blogs/aws/auto-scale-dynamodb-with-dynamic-dynamodb/)