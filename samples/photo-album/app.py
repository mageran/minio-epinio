import os
from flask import Flask, send_from_directory, request
import boto3
from base64 import b64encode, b64decode
import minio
from get_image_size import get_image_size 



app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=minio.params['endpoint_url'],
        aws_access_key_id=minio.params['accesskey'],
        aws_secret_access_key=minio.params['secretkey'],
        verify=False
    )


def data_response(obj):
    return {'data': obj}


_image_suffixes = ['JPG', 'JPEG', 'GIF', 'PNG']


def _is_image(name):
    _, ext = os.path.splitext(name)
    flist = list(filter(lambda suffix: (ext == f'.{suffix.lower()}') or (
        ext == f'.{suffix.upper()}'), _image_suffixes))
    return len(flist) > 0


@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)


@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


def _get_object_metadata(key, size):
    bucket = minio.params['s3_bucket_name']
    s3client = get_s3_client()
    mdata = s3client.get_object(Bucket=bucket, Key=key)
    size = mdata['ContentLength']
    get_image_size(mdata['Body'].read(), size, mdata)
    mdata['Body'] = None
    mdata['IsImage'] = _is_image(key)
    mdata['Key'] = key
    _, mdata['FileExtension'] = os.path.splitext(key)
    mdata['ResponseMetadata'] = None
    return {'Metadata': mdata}


@app.route('/api/object')
def list_objects_in_bucket():
    bucket = minio.params['s3_bucket_name']
    s3client = get_s3_client()
    objects = []
    try:
        objects = s3client.list_objects(Bucket=bucket)['Contents']
        for object in objects:
            key = object['Key']
            size = object['Size']
            mdata = _get_object_metadata(key, size)['Metadata']
            object['Metadata'] = mdata
    except:
        pass
    return data_response(objects)


@app.route('/api/object/<key>/$metadata')
def get_object_metadata(key):
    return _get_object_metadata(key, 100)


@app.route('/api/object/<key>')
def get_object_data(key):
    bucket = minio.params['s3_bucket_name']
    s3client = get_s3_client()
    obj_data = s3client.get_object(Bucket=bucket, Key=key)['Body'].read()
    enc_obj_data = b64encode(obj_data)
    return str(enc_obj_data, 'utf-8')


@app.post('/api/object/<key>')
def create_data_object(key):
    print(f'creating bucket object with key {key}...')
    bucket = minio.params['s3_bucket_name']
    s3client = get_s3_client()
    bytes = b64decode(request.data)
    s3client.put_object(Bucket=bucket, Key=key, Body=bytes)
    return data_response(True)


@app.delete('/api/object/<key>')
def delete_data_object(key):
    print(f'deleting bucket object with key {key}...')
    bucket = minio.params['s3_bucket_name']
    s3client = get_s3_client()
    s3client.delete_object(Bucket=bucket, Key=key)
    return data_response(True)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
