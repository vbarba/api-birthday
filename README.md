# api-birthday

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- api_birthday - Code for the application's Lambda function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.
- codepipeline.yaml - A template that defines the applications deploy pipeline

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project.


The app is a simple 'hello world' app that stores the username date of birth in a database with a PUT request with the following format:

```
Description: Saves/updates the given user’s name and date of birth in the database.
Request: PUT /hello/<username> { “dateOfBirth”: “YYYY-MM-DD” }
Response: 204 No Content
```

And returns a nice message calculating the days left for the user birthday with a GET request.
```
Description: Returns hello birthday message for the given user
Request: Get /hello/<username>
Response: 200 OK
Response Examples:
A. If username’s birthday is in N days:
{ “message”: “Hello, <username>! Your birthday is in N day(s)”
}
B. If username’s birthday is today:
{ “message”: “Hello, <username>! Happy birthday!” }
```

## Architecture diagram

This is a simple 'hello world' app with a typical serverless architecture. There is a public API Gateway that triggers the lambda function for PUT / GET events.
The database used is a serverless DynamoDB. All the infrastructure is defined in the `template.yaml' file as IaC.

![image](https://user-images.githubusercontent.com/924020/137930939-65f7ce15-ccd8-4b0f-89d5-e974fa1094c4.png)

## Deploy

The `codepipeline.yaml` template provides a pipeline for CI/CD for this app. It uses the best-practice for Serverless deployments defined here:

https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-generating-example-ci-cd-codepipeline.html

The pipeline have the following stages:

### Source

After a commit is pushed to the `main` branch in the repository the pipeline is triggered and the code is downloaded by the AWS Codepipeline service

![Screenshot 2021-10-19 at 16 18 24](https://user-images.githubusercontent.com/924020/137931265-97079247-8e74-45be-914d-dda12ae6e5b3.png)


### UpdatePipeline

As the pipeline is also defined as IaC any change on the pipeline at applied first.

![Screenshot 2021-10-19 at 16 19 24](https://user-images.githubusercontent.com/924020/137931281-fd90bd64-1ec7-4b13-b88b-e885d77890d8.png)

### UnitTest

The UnitTest are run. You can find it in the `tests/unit` folder.

![Screenshot 2021-10-19 at 16 19 54](https://user-images.githubusercontent.com/924020/137931304-d059e15a-466e-4a99-88f4-b869127bb596.png)

### BuildAndPackage

The code is build and all the necessary files for deployment are generated

![Screenshot 2021-10-19 at 17 04 38](https://user-images.githubusercontent.com/924020/137938351-d17775c1-6d03-4580-8ec7-8b30ee5ca24e.png)

### DeployTest and Integration Test

The code is deployed to the *Test* environment.

This stage runs the integration test. The purpose of this is test that the integration between the apigateway-lambda-dynamodb works in a AWS environment.

![Screenshot 2021-10-19 at 17 05 02](https://user-images.githubusercontent.com/924020/137938336-9bf84399-bf83-4f3a-b73f-a1ddd708fc8c.png)


### Deploy Prod

The code is deployed to the *Prod* environment. As this is a Lambda substitution there is no interruption. Exists more advanced deployment methods that are described here but out of scope for this project:

https://github.com/aws/serverless-application-model/blob/master/docs/safe_lambda_deployments.rst

![Screenshot 2021-10-19 at 17 05 27](https://user-images.githubusercontent.com/924020/137938307-66013cd7-8d7e-40ce-847e-571291dea9f1.png)


## Use the SAM CLI to build and test locally

The SAM CLI can emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
api-birthday$ sam local start-api
api-birthday$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        ApiBirthday:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```


## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
api-birthday$ sam logs -n HelloWorldFunction --stack-name api-birthday --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Local Unit Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
api-birthday$ pip install -r tests/requirements.txt --user
# unit test
api-birthday$ python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
api-birthday$ AWS_SAM_STACK_NAME=<stack-name> python -m pytest tests/integration -v
```

## Cleanup

To delete the application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name api-birthday
```

