#!/bin/bash

# Usage: ./minio-upload my-bucket my-file.zip

bucket=$1
file=$2

echo "file=$file"
host=10.0.0.96:9000
s3_key='minioadmin'
s3_secret='minioadmin'

resource="/${bucket}/${file}"
content_type="application/octet-stream"
date=`date -R`
echo $date

_signature="PUT\n\n${content_type}\n${date}\n${resource}"
echo "_signature="$_signature
signature=`echo -en ${_signature} | openssl sha1 -hmac ${s3_secret} -binary | base64`
echo "signature="$signature
curl -X PUT -v -T "${file}" \
          -H "Host: ${host}" \
          -H "Date: ${date}" \
          -H "Content-Type: ${content_type}" \
          -H "Authorization: AWS ${s3_key}:${signature}" \
          http://${host}${resource}