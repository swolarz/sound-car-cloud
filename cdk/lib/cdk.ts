import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from "@aws-cdk/aws-cognito";
import * as s3 from "@aws-cdk/aws-s3";
import * as cloudfront from "@aws-cdk/aws-cloudfront";
import * as iam from "@aws-cdk/aws-iam";

export class SoundCarCloudStack extends cdk.Stack {
    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);

      const userPool = new cognito.UserPool(this, id + "SoundCarCloudStackUserPool", {
        signInAliases: {
          username: true,
          email: true,
        },
        autoVerify: {
          email: true,
          phone: false,
        },
        selfSignUpEnabled: true,
        userVerification: {
          emailSubject: 'Verify your email for our awesome app!',
          emailBody: 'Hello, Thanks for signing up to our awesome app! Your verification code is {####}',
          emailStyle: cognito.VerificationEmailStyle.CODE,
          smsMessage: 'Hello, Thanks for signing up to our awesome app! Your verification code is {####}',
        }, 
        passwordPolicy: {
              minLength: 6
        }
      });

      const lambdaCodeAsset = lambda.Code.fromAsset('../lambda/src');
      const helloLambda = new lambda.Function(this, "HelloHandler", {
        runtime: lambda.Runtime.PYTHON_3_7,
        code: lambdaCodeAsset,
        handler: "lambda.handler"
      });

      helloLambda.addToRolePolicy(new iam.PolicyStatement(
        {
          resources: [userPool.userPoolArn],
          actions: [
            "cognito-idp:AdminUserGlobalSignOut",
            "cognito-idp:AdminGetUser"
          ]
        })
      );
  
      const api = new apigateway.RestApi(this, id + "HelloAPI", {
        defaultCorsPreflightOptions: {
          allowOrigins: ["*"],
          allowHeaders: ['Authorization', "Access-Control-Allow-Origin"]
        }
      });
      const helloLambdaIntegration = new apigateway.LambdaIntegration(helloLambda, {
        proxy: true
      });

      const auth = new apigateway.CfnAuthorizer(this, 'APIGatewayAuthorizer', {
        name: 'customer-authorizer',
        identitySource: 'method.request.header.Authorization',
        providerArns: [userPool.userPoolArn],
        restApiId: api.restApiId,
        type: apigateway.AuthorizationType.COGNITO,
      });

      const getOnRoot = api.root.addMethod('GET', helloLambdaIntegration, {
        authorizationType: apigateway.AuthorizationType.COGNITO,
        authorizer: { authorizerId: auth.ref },
      });

    const uiBucket = new s3.Bucket(this, 'SoundCarCloudUIBucket', {
      publicReadAccess: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
    const uiBucketName = uiBucket.bucketName;
    const cloudFrontOia = new cloudfront.OriginAccessIdentity(this, 'OIA', {
      comment: `OIA for ${uiBucket.bucketName}`
    });
    const distribution = new cloudfront.CloudFrontWebDistribution(this, 'SoundCarCloudUIDistribution', {
      originConfigs: [
        {
          s3OriginSource: {
            s3BucketSource: uiBucket,
            originAccessIdentity: cloudFrontOia
          },
          behaviors: [{isDefaultBehavior: true}]
        }
      ]
    });
    
    const appUrl = "https://" + distribution.domainName;

    const cfnUserPoolDomain = new cognito.CfnUserPoolDomain(this, "CognitoDomain", {
      domain: "auth-" + this.account + "-" + this.region,
      userPoolId: userPool.userPoolId
    });

    const cfnUserPoolClient = new cognito.CfnUserPoolClient(this, "CognitoAppClient", {
      supportedIdentityProviders: ["COGNITO"],
      clientName: "Web",
      allowedOAuthFlowsUserPoolClient: true,
      allowedOAuthFlows: ["code"],
      allowedOAuthScopes: ["phone", "email", "openid", "profile"],
      explicitAuthFlows: ["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH", "ALLOW_USER_PASSWORD_AUTH"],
      preventUserExistenceErrors: "ENABLED",
      generateSecret: false,
      refreshTokenValidity: 1,
      callbackUrLs: [appUrl],
      logoutUrLs: [appUrl],
      userPoolId: userPool.userPoolId
    });

    // outputs for aws-exports file
    new cdk.CfnOutput(this, "RegionOutput", {
      description: "Region",
      value: this.region
    });

    new cdk.CfnOutput(this, "CognitoDomainOutput", {
      description: "Cognito Domain",
      value: cfnUserPoolDomain.domain
    });

    new cdk.CfnOutput(this, "UserPoolIdOutput", {
      description: "UserPool ID",
      value: userPool.userPoolId
    });

    new cdk.CfnOutput(this, "AppClientIdOutput", {
      description: "App Client ID",
      value: cfnUserPoolClient.ref
    });

    new cdk.CfnOutput(this, "APIUrlOutput", {
      description: "API URL",
      value: api.url
    });

    new cdk.CfnOutput(this, "AppUrl", {
      description: "The frontend app's URL",
      value: appUrl
    });

    new cdk.CfnOutput(this, "UIBucketName", {
      description: "The frontend app's bucket name",
      value: uiBucketName
    });
  }
}