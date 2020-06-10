import aws_generated_exports from './autoGenConfig';
import { Auth } from "aws-amplify"

const awsmobile = {
  Auth: {
    region: aws_generated_exports.regio,
    userPoolId: aws_generated_exports.cognitoUserPoolId,
    userPoolWebClientId:  aws_generated_exports.cognitoUserPoolAppClientId,
  },
  API: {
    endpoints: [
      {
        name: "hello",
        endpoint: aws_generated_exports.apiUrl,
        custom_header: async () => { 
          return { 
            Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}`
          }
        }
      },
      {
        name: "uploadPhotos",
        endpoint: aws_generated_exports.uploadPhotosPath,
        custom_header: async () => { 
          return { 
            Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}`,
            "Content-Type": 'application/json' 
          }
        }
      }
    ],
  },
};


export default awsmobile;
