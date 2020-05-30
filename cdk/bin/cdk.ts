#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { SoundCarCloudStack } from '../lib/cdk';

const app = new cdk.App();
new SoundCarCloudStack(app, 'SoundCarCloudStack');
