
# file final URL: https://pcdc-gen3-dictionaries.s3.amazonaws.com/schema.json
aws s3 cp “/Users/lgraglia/Projects/GEN3_dev/dev_tools/datadictionary/dictionaryutils/artifacts/schema.json” s3://pcdc-gen3-dictionaries/ --acl public-read



# CMD to edit if already uploaded
# aws s3api put-object-acl --bucket awsexamplebucket --key exampleobject --acl public-read