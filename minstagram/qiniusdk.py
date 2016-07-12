# -*- coding:utf-8 -*-

from minstagram import app
from qiniu import Auth, put_data, put_stream
import os

access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']
bucket_name = app.config['QINIU_BUCKET_NAME']
q = Auth(access_key, secret_key)
domain_prefix = app.config['QINIU_DOMAIN_PREFIX']

def qiniu_uplod_file(sfile, filename):
	token = q.upload_token(bucket_name, filename)
	ret, info = put_data(token, filename, sfile.stream)
	#ret, info = put_stream(token, filename, sfile.stream, "qiniu", os.fstat(sfile.srteam.fileno()).st_size)

	if info.status_code == 200:
		return domain_prefix + filename

	return None

