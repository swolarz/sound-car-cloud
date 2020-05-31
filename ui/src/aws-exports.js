import aws_generated_exports from './autoGenConfig';

const awsmobile = {
  "aws_project_region": aws_generated_exports.region,
  "aws_cognito_region": aws_generated_exports.region,
  "aws_user_pools_id": aws_generated_exports.cognitoUserPoolId,
  "aws_user_pools_web_client_id": aws_generated_exports.cognitoUserPoolAppClientId,
  "oauth": {}
};


export default awsmobile;
