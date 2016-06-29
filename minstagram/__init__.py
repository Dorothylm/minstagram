# -*- encoding=UTF-8 -*-

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('app.conf')

from minstagram import views, models