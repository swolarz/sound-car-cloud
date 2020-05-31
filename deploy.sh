source ./env.sh

cd cdk

cdk deploy
npm run generate-config -- "${STACK_NAME}" "${STACK_REGION}" ../ui/src/autoGenConfig.js

#cd ./ui

#npm run build &> /dev/null

#aws s3 sync --delete ./build/ "s3://${BUCKET_NAME}" &> /dev/null