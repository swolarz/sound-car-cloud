source ./env.sh

cd cdk

cdk bootstrap
cdk deploy
npm run generate-config -- "${STACK_NAME}" "${STACK_REGION}" ../ui/src/autoGenConfig.js

cd ../ui

export BUCKET_NAME=$(node --print "require('./src/autoGenConfig.js').uiBucketName")
npm run build
aws s3 sync --delete ./dist/ "s3://${BUCKET_NAME}"