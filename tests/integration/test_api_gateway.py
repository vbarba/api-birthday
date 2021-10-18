import os
from unittest import TestCase
import json
import boto3
import requests
from datetime import datetime,timedelta


"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway(TestCase):
    api_endpoint: str

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )

        return stack_name

    def setUp(self) -> None:

        stack_name = TestApiGateway.get_stack_name()

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
            ) from e

        stacks = response["Stacks"]

        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "ApiBirthdayApi"]
        self.assertTrue(api_outputs, f"Cannot find output ApiBirthdayApi in stack {stack_name}")

        self.api_endpoint = api_outputs[0]["OutputValue"]

    def test_api_gateway_put(self):
        """
        Call the API Gateway endpoint and check the response
        """
        tomorrow = datetime.now()+ timedelta(days=-1)
        response_put = requests.put(self.api_endpoint+'/testuser', data=json.dumps({"dateOfBirth": tomorrow.strftime('%Y-%m-%d')}), headers={"Content-Type": "application/json"})
        self.assertEqual(response_put.status_code, 200)

    def test_api_gateway_get(self):
        response_get = requests.get(self.api_endpoint+'/testuser')
        self.assertDictEqual(response_get.json(), {"message": "Hello, testuser! Your birthday is in 364 day(s)"})
