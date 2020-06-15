source ./env.sh

cd cdk

npm run cdk bootstrap
npm run cdk synth > cloudformation-synth-output.yml
npm run cdk deploy
npm run generate-config -- "${STACK_NAME}" "${STACK_REGION}" ../ui/src/autoGenConfig.js

cd ../ui

export BUCKET_NAME=$(node --print "require('./src/autoGenConfig.js').uiBucketName")
npm install
npm run build
aws s3 sync --delete ./dist/ "s3://${BUCKET_NAME}"

