import * as aws from "aws-sdk";
import {CloudFormation} from "aws-sdk";

export class Utils {
    static async getStackOutputs(stackName: string, stackRegion: string): Promise<CloudFormation.Output[]> {
      aws.config.region = stackRegion;
      const cfn = new aws.CloudFormation();
      const result = await cfn.describeStacks({StackName: stackName}).promise();
      return result.Stacks![0].Outputs!;
    }

    static getEnv(variableName: string) {
      const variable = process.env[variableName];
      if (!variable) {
        throw new Error(`${variableName} environment variable must be defined`);
      }
      return variable
    }
}