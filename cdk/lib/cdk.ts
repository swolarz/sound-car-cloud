import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as apigateway from '@aws-cdk/aws-apigateway';

export class SoundCarCloudStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);
  
      const lambdaCodeAsset = lambda.Code.fromAsset('../lambda/src');
  
      const helloLambda = new lambda.Function(this, "HelloHandler", {
        runtime: lambda.Runtime.PYTHON_3_7,
        code: lambdaCodeAsset,
        handler: "lambda.handler"
      });
  
      const lambdaApi = new apigateway.LambdaRestApi(this, "HandlerApi", {
        handler: helloLambda
      });
    }
  }