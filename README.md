# Python Scraper using AWS Services
A cloud scraper Lambda function(Python3.7), S3, SQS
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
## General info
This project is scraper to srape categories, faculties and courses only from Vlerick university.
- SQS: storing university base url to scrape
- Lambda function: fetching and parsing web pages
- S3: Simple storage service to store final json files
- IAM: Identity and Access Management to allow you have access to specific AWS services by creating roles for needed
 services 
- AWS SDK: Python is using boto3 library to help integrate SQS or S3 service to Lambda function
## Technologies
Project is created with:
* Python: 3.7
## Setup
### Step 1 - Install boto3: 
  To run this project, install boto3 locally using the package manager pip:
```Terminal
# If your local default python version is 3.X
$ pip install boto3

# If you have multiple python versions in local(MAC python2.X and python3.X),
# 2.X is the default version.
$ pip3 install boto3
```
- step 2: Create IAM role by specifying trust policy inline
    + role name: sqs-lambda-s3
    + after creating IAM role, the output will contain Arn. __Remember to copy the Arn in the output__
```Terminal
$ aws iam create-role --role-name sqs-lambda-s3 --assume-role-policy-document '{"Version": "2012-10-17","Statement
": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
```
- step 3: Attach policies to the role to allow lambda function execution and let cloudwatch record logs for the lambda
 function, lambda function write files to S3 and SQS trigger Lambda function.
  + AWSLambdaBasicExecutionRole
  + AmazonSQSFullAccess
  + AmazonS3FullAccess
```Terminal
$aws iam attach-role-policy --role-name sqs-lambda-s3 --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
$aws iam attach-role-policy --role-name sqs-lambda-s3 --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
$aws iam attach-role-policy --role-name sqs-lambda-s3 --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```
- step 4: Zip files for deployment
```Terminal
$ zip vlerick_3399_EUR.zip .
``` 
    
- step5: Create lambda function with the role create in __step 2__
        Modify the below arn resource
```Terminal
$ aws lambda create-function --function-name vlerick_scraper --zip-file fileb://vlerick_3399_EUR.zip --handler
 lambda_function.lambda_handler --runtime python3.7 --role arn:aws:iam::your-account-id:role/sqs-lambda-s3
```

- step 6: Create three S3 buckets for storing category, faculty and detail respectively. You can name what ever you
 want.
    + university-categories
    + university-faculties
    + university-details
```Terminal
$ aws s3 mb s3://university-categories
$ aws s3 mb s3://university-faculties
$ aws s3 mb s3://university-details
```
You can check if the buckets are created successfully by list them out

```Terminal
$ aws s3 ls
```

- step 7: Create Environment variables to lambda function
```Terminal
$ aws lambda update-function-configuration --function-name aws lambda update-function-configuration --function-name
 vlerick_scraper --environment '{"Variables":{"s3_category_bucket_name":"university-categories
", "s3_detail_bucket_name":"university-details","s3_faculty_bucket_name":"university-faculties"}}'
```

- step 8: Create a sqs queue and set delayseconds to 2s. __remember copy sqs Arn__
```Terminal
$ aws sqs create-queue --queue-name scraper-queue --attributes DelaySeconds=2
```

- step 9: Configure  sqs as lambda trigger
[Create event map](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource)

```Terminal
$ aws lambda create-event-source-mapping --function-name my-function --batch-size 5 \
--maximum-batching-window-in-seconds 60 \
--event-source-arn arn:aws:sqs:us-east-2:123456789012:my-queue
```
