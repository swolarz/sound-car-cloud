import {Utils} from "./utils";
import * as fs from "fs";

class GenerateCognitoConfig {
    async generateConfig(stackName: string, stackRegion: string, filePath: string) {

        const outputs = await Utils.getStackOutputs(stackName, stackRegion);
        const outputsByName = new Map<string, string>();
        for (let output of outputs) {
          outputsByName.set(output.OutputKey!, output.OutputValue!);
        }
    
        const region = outputsByName.get("RegionOutput");
        const cognitoDomainPrefix = outputsByName.get("CognitoDomainOutput");
        const userPoolId = outputsByName.get("UserPoolIdOutput");
        const appClientId = outputsByName.get("AppClientIdOutput");
        const apiURL = outputsByName.get("APIUrlOutput");
        const appURL = outputsByName.get("AppUrl");
        const uiBucketName = outputsByName.get("UIBucketName") || "";
    
        const cognitoDomain = `${cognitoDomainPrefix}.auth.${region}.amazoncognito.com`;
        const params = {
          cognitoDomain: cognitoDomain,
          region: region,
          cognitoUserPoolId: userPoolId,
          cognitoUserPoolAppClientId: appClientId,
          apiUrl: apiURL,
          appUrl: appURL,
          uiBucketName: uiBucketName
        };
    
        const autoGenConfigFile = "// this file is auto generated, do not edit it directly\n" +
          "module.exports = " + JSON.stringify(params, null, 2);

          fs.writeFileSync(filePath, autoGenConfigFile);
        }
    }

const stackName = process.argv[2];
if (!stackName) {
  throw new Error("stack name is required");
}
const stackRegion = process.argv[3];
if (!stackName) {
  throw new Error("stack region is required");
}
const filePath = process.argv[4];
if (!stackName) {
  throw new Error("file path is required");
}

new GenerateCognitoConfig().generateConfig(stackName, stackRegion, filePath);