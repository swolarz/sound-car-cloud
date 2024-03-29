#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { SoundCarCloudStack } from '../lib/cdk';
import {Utils} from "../lib/utils";

const app = new cdk.App();
const stackName = Utils.getEnv("STACK_NAME");
const verifiedEmail = Utils.getEnv("VERIFIED_MAIL");
const verifiedEmailRegion = Utils.getEnv("VERIFIED_MAIL_REGION");
const stack = new SoundCarCloudStack(app, stackName, verifiedEmail, verifiedEmailRegion);

stack.templateOptions.transforms = ["AWS::Serverless-2016-10-31"];