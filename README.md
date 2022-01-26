# CantoTranslate API Server

This repository hosts the API Server for CantoTranslate.

This was created because there didn't exist an API Server for fetching Cantonese words.

### Prerequisites

* This assumes your DynamoDB has a table with entries with the schema:

```
@dataclass
class Definition:
    traditional: str
    simplified: str
    jyutping: str
    pinyin: str
    definition: str
```

### Setup

1. Set up an S3 bucket where you can upload the swagger.yml to

1. Upload swagger.yml to S3 bucket

```
S3_BUCKET=<name of bucket>
aws s3 cp swagger.yml s3://$S3_BUCKET/swagger.yaml
```

1. Deploy the infrastructure

```
sam deploy --template-file template.yml --s3-bucket=$S3_BUCKET --parameter-overrides BucketName=$S3_BUCKET
```