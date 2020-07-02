import aws_exports from './autoGenConfig';
import { Auth } from "aws-amplify"

import * as url from 'url';


const awsmobile = {
  Auth: {
    region: aws_exports.regio,
    userPoolId: aws_exports.cognitoUserPoolId,
    userPoolWebClientId:  aws_exports.cognitoUserPoolAppClientId,
  },
  API: {
    endpoints: [
      {
        name: "carPhotosUpload",
        endpoint: url.resolve(aws_exports.apiUrl, "car-photos"),
        custom_header: async () => { 
          return { 
            Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}`,
            "Content-Type": 'application/json' 
          }
        }
      },
      {
        name: "carUpload",
        endpoint: url.resolve(aws_exports.apiUrl, 'cars'),
        custom_header: async () => { 
          return { 
            Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}`,
            "Content-Type": 'application/json' 
          }
        },
      },
      {
        name: "carFetch",
        endpoint: url.resolve(aws_exports.apiUrl, 'cars'),
        custom_header: async () => { 
          return { 
            "Content-Type": 'application/json' 
          }
        },
      },
    ],
  },
};


export default awsmobile;
