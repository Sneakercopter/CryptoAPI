# CryptoAPI
Binance API implementation to track crypto performance, example is a Docker image intended for AWS Lambda functions but the `Binance.py` library can easily be added to custom projects.

## Building and Deploying to Lambda Function
- Fill in your secrets into `Binance.py`
- `docker build .` in the project directory. 
- Tag the built image using `docker tag`
- Push the built image to AWS ECR Registry
- Create a new lambda function from the ECR Registry image and the API will deploy automatically
- Add an API Gateway Input and allow GET requests through it.
- API will now return all Binance data in a `JSON` response.
