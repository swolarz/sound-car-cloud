import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from "@aws-cdk/aws-cognito";

export class SoundCarCloudStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);

      const authorizationHeaderName = "Authorization";
      const userPool = new cognito.UserPool(this, id + "SoundCarCloudStackPool", {
          passwordPolicy: {
              minLength: 6
          },
      });

      const lambdaCodeAsset = lambda.Code.fromAsset('../lambda/src');
  
      const helloLambda = new lambda.Function(this, "HelloHandler", {
        runtime: lambda.Runtime.PYTHON_3_7,
        code: lambdaCodeAsset,
        handler: "lambda.handler",
        environment: {
            USER_POOL_ID: userPool.userPoolId,
            AUTHORIZATION_HEADER_NAME: authorizationHeaderName,
        }
      });
  
      const api = new apigateway.RestApi(this, id + "HelloAPI");
      const helloLambdaIntegration = new apigateway.LambdaIntegration(helloLambda);

      const auth = new apigateway.CfnAuthorizer(this, 'APIGatewayAuthorizer', {
        name: 'customer-authorizer',
        identitySource: 'method.request.header.Authorization',
        providerArns: [userPool.userPoolArn],
        restApiId: api.restApiId,
        type: apigateway.AuthorizationType.COGNITO,
    });

    const post = api.root.addMethod('GET', helloLambdaIntegration, {
      authorizationType: apigateway.AuthorizationType.COGNITO,
      authorizer: { authorizerId: auth.ref }
    });
  }
}