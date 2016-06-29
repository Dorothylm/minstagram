# -*- encoding=UTF-8 -*-

from minstagram import app

@app.route('/')
def index():
	return 'hello'