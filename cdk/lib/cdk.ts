import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as cognito from "@aws-cdk/aws-cognito";
import * as s3 from "@aws-cdk/aws-s3";
import * as cloudfront from "@aws-cdk/aws-cloudfront";
import * as sqs from "@aws-cdk/aws-sqs"
import * as s3n from "@aws-cdk/aws-s3-notifications";
import * as sqses from "@aws-cdk/aws-lambda-event-sources";
import * as elasticsearch from '@aws-cdk/aws-elasticsearch';
import * as customresource from '@aws-cdk/custom-resources';
import * as iam from '@aws-cdk/aws-iam';
import { Policy } from '@aws-cdk/aws-iam';


export class SoundCarCloudStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, fromEmail: string, sesRegion: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const authorizationHeaderName = 'Authorization';
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

    // Elasticsearch
    const elasticsearchDomain = new elasticsearch.CfnDomain(this, "DomainElasticsearchCluster", {
      domainName: 'sound-car-cloud-es',
      elasticsearchClusterConfig: {
        instanceCount: 1,
        instanceType: 't2.small.elasticsearch'
      },
      ebsOptions: {
        ebsEnabled: true,
        volumeSize: 10
      },
      // encryptionAtRestOptions: {
        // enabled: true
      // },
      nodeToNodeEncryptionOptions: {
        enabled: true
      },
      elasticsearchVersion: '7.4'
    });

    // Elasticsearch index initialization
    const carStorageCodeAsset = lambda.Code.fromAsset('../lambda/src/car-storage');
    const initCarStorageIndexLambda = new lambda.Function(this, 'InitCarStorageIndexHandler', {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: carStorageCodeAsset,
      handler: 'init_cars_index.handler',
      timeout: cdk.Duration.minutes(1),
      environment: {
        ELASTICSEARCH_SERVICE_ENDPOINT: elasticsearchDomain.attrDomainEndpoint,
        USER_POOL_ID: userPool.userPoolId,
        AUTHORIZATION_HEADER_NAME: authorizationHeaderName
      }
    });
    initCarStorageIndexLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "es:*" ],
        resources: [ elasticsearchDomain.attrArn + '*' ]
      })
    );

    new customresource.AwsCustomResource(this, 'initCarStorageEsIndexResource_v1', {
      onCreate: {
        service: 'Lambda',
        action: 'invoke',
        parameters: {
          FunctionName: initCarStorageIndexLambda.functionName
        },
        physicalResourceId: { id: 'initCarStorageEsIndex' }
      },
      policy: {
        statements: [
          new iam.PolicyStatement({
            actions: ['*'],
            resources: ['*']
          })
        ]
      }
    });

    // Cars CRUD lambdas
    const carInsertLambda = new lambda.Function(this, 'CarStorageInsertHandler', {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: carStorageCodeAsset,
      handler: 'car_insert.handler',
      environment: {
        ELASTICSEARCH_SERVICE_ENDPOINT: elasticsearchDomain.attrDomainEndpoint,
        USER_POOL_ID: userPool.userPoolId,
        AUTHORIZATION_HEADER_NAME: authorizationHeaderName
      }
    });
    carInsertLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "es:*" ],
        resources: [ elasticsearchDomain.attrArn + '*' ]
      })
    );

    // Cars CRUD lambdas
    const carEditLambda = new lambda.Function(this, 'CarStorageEditHandler', {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: carStorageCodeAsset,
      handler: 'car_insert.put_car_handler',
      environment: {
        ELASTICSEARCH_SERVICE_ENDPOINT: elasticsearchDomain.attrDomainEndpoint,
        USER_POOL_ID: userPool.userPoolId,
        AUTHORIZATION_HEADER_NAME: authorizationHeaderName
      }
    });
    carEditLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "es:*" ],
        resources: [ elasticsearchDomain.attrArn + '*' ]
      })
    );

    const carGetLambda = new lambda.Function(this, 'CarStorageGetHandler', {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: carStorageCodeAsset,
      handler: 'car_insert.get_car_handler',
      environment: {
        ELASTICSEARCH_SERVICE_ENDPOINT: elasticsearchDomain.attrDomainEndpoint,
      }
    });
    carGetLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "es:ESHttpGet" ],
        resources: [ elasticsearchDomain.attrArn + '*' ]
      })
    );

    const assignPhotoToCar = new lambda.Function(this, 'AssignPhotoToCar', {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: carStorageCodeAsset,
      handler: 'car_insert.assign_photo_to_car',
      environment: {
        ELASTICSEARCH_SERVICE_ENDPOINT: elasticsearchDomain.attrDomainEndpoint,
      }
    });
    assignPhotoToCar.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "es:*" ],
        resources: [ elasticsearchDomain.attrArn + '*' ]
      })
    );


    // Lambda functions
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

    helloLambda.addToRolePolicy(new iam.PolicyStatement(
      {
        resources: [userPool.userPoolArn],
        actions: [
          "cognito-idp:AdminUserGlobalSignOut",
          "cognito-idp:AdminGetUser"
        ]
      })
    );

    // Rest API
    const api = new apigateway.RestApi(this, id + "HelloAPI", {
      defaultCorsPreflightOptions: {
        allowOrigins: ["*"],
        allowHeaders: ['Authorization', "Access-Control-Allow-Origin", "Content-Type"]
      }
    });

    // Cognito Authorization
    const auth = new apigateway.CfnAuthorizer(this, 'APIGatewayAuthorizer', {
      name: 'customer-authorizer',
      identitySource: 'method.request.header.Authorization',
      providerArns: [userPool.userPoolArn],
      restApiId: api.restApiId,
      type: apigateway.AuthorizationType.COGNITO,
    });

    const globalCognitoSecuredMethodOptions = {
      authorizationType: apigateway.AuthorizationType.COGNITO,
      authorizer: { authorizerId: auth.ref },
    }

    // Lambda Rest Api
    const helloLambdaIntegration = new apigateway.LambdaIntegration(helloLambda,);
    const carInsertLambdaIntegration = new apigateway.LambdaIntegration(carInsertLambda);
    const carEditLambdaIntegration = new apigateway.LambdaIntegration(carEditLambda);
    const carGetLambdaIntegration = new apigateway.LambdaIntegration(carGetLambda);

    api.root.addMethod('GET', helloLambdaIntegration, globalCognitoSecuredMethodOptions);
    const carsHandlerPath = "cars";
    
    const carsHandler = api.root.addResource(carsHandlerPath);
    carsHandler.addMethod('POST', carInsertLambdaIntegration, globalCognitoSecuredMethodOptions);
    
    const carHandler = carsHandler.addResource('{car_id}')
    carHandler.addMethod('PUT', carEditLambdaIntegration, globalCognitoSecuredMethodOptions);
    carHandler.addMethod('GET', carGetLambdaIntegration);

    // Web UI
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
        },
      ],
      defaultRootObject: 'index.html',
      errorConfigurations: [
        {
          errorCode: 403,
          responseCode: 200,
          responsePagePath: '/index.html'
        },
        {
          errorCode: 404,
          responseCode: 200,
          responsePagePath: '/index.html'
        },
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

    const photosBucket = new s3.Bucket(this, 'SoundCarCloudUIBucketPhotos', {
      publicReadAccess: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const uploadPhotosLambdaEnvironment = {
      Bucket: photosBucket.bucketName,
      GetCarLambda: carGetLambda.functionArn 
    };

    const uploadPhotosLambda = new lambda.Function(this, "UploadPhotosHandler", {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: lambda.Code.fromAsset('../lambda/src/upload'),
      handler: "photosUpload.upload",
      environment: uploadPhotosLambdaEnvironment
    });

    uploadPhotosLambda.addToRolePolicy(new iam.PolicyStatement({
      resources: [ carGetLambda.functionArn ],
      actions: [ "lambda:InvokeFunction" ]
    }))

    photosBucket.grantWrite(uploadPhotosLambda);
    
    const photosUploadPath = "photosUpload";
    const photosUpload = api.root.addResource(photosUploadPath);
    photosUpload.addMethod("POST", 
      new apigateway.LambdaIntegration(uploadPhotosLambda),
      globalCognitoSecuredMethodOptions
    );

    const createdPhotosQueue = new sqs.Queue(this, "CreatedPhotosQuque", {
      visibilityTimeout: cdk.Duration.minutes(5),
    });
    photosBucket.addObjectCreatedNotification(new s3n.SqsDestination(createdPhotosQueue));

    const photoRecognizerEnvironment = {
      FromEmail: fromEmail,
      SESRegion: sesRegion,
      AssignPhotoToCarLambdaArn: assignPhotoToCar.functionArn,
      GetCarLambda: carGetLambda.functionArn,
      UserPoolId: userPool.userPoolId
    };

    const photoRecognizer = new lambda.Function(this, "PhotoRecognizer", {
      runtime: lambda.Runtime.PYTHON_3_7,
      code: lambda.Code.fromAsset('../lambda/src/validators'),
      handler: "carOnPhotoValidator.validate",
      environment: photoRecognizerEnvironment,
    });
    photoRecognizer.addEventSource(new sqses.SqsEventSource(createdPhotosQueue, { batchSize: 1 }));
    photosBucket.grantRead(photoRecognizer);
    photoRecognizer.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["rekognition:DetectLabels"],
        resources: ["*"],
    }));

    photoRecognizer.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["ses:SendEmail"],
        resources: ["*"],
    }));

    photoRecognizer.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [ "lambda:InvokeFunction" ],
        resources: [ assignPhotoToCar.functionArn, carGetLambda.functionArn ],
    }));

    photoRecognizer.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["cognito-idp:ListUsers"],
        resources: [ userPool.userPoolArn ],
    }));

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

    new cdk.CfnOutput(this, "UploadPhotosPath", {
      description: "UploadPhotosPath",
      value: api.url + photosUploadPath
    });

    new cdk.CfnOutput(this, "CarsHandlerPath", {
      description: "CarsHandlerPath",
      value: api.url + carsHandlerPath
    });

    new cdk.CfnOutput(this, "PhotoBucketUrl", {
      description: "PhotoBucketUrl",
      value: `https://${photosBucket.bucketName}.s3.amazonaws.com/` 
    });
  }
}
