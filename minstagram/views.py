# -*- encoding=UTF-8 -*-

from minstagram import app, db
from flask import  render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from models import Image, User, Comment
import hashlib, random, json, uuid, os
from flask_login import login_required, login_user, logout_user, current_user
from qiniusdk import qiniu_uplod_file

@app.route('/')
def index():
	paginate = Image.query.order_by('id desc').paginate(page=1, per_page=10, error_out=False)
	return render_template('index.html', images=paginate.items, has_next=paginate.has_next)


@app.route('/index/<int:page>/<int:per_page>/')
def index_image(page, per_page):
	paginate = Image.query.order_by('id desc').paginate(page=page, per_page=per_page, error_out=False)

	map = {'has_next':paginate.has_next}
	images = []
	for img in paginate.items:
		comments = []
		#最多取两条评论
		for i in range(0, min(2, img.comments.count())):
			comment = img.comments[i]
			comments.append({'username':comment.user.username,
							 'user_id':comment.user_id,
							 'content':comment.content})

		user = User.query.filter_by(id=img.user_id).first()
		imgvo = {'created_time':str(img.created_time),
				 'user_id':img.user_id,
				 'head_url':user.head_url,
				 "username":user.username,
				 'image_id':img.id,
				 'image_url':img.url,
				 'comments_count':img.comments.count(),
				 'comments':comments}
		images.append(imgvo)
	map['images'] = images

	return json.dumps(map)

@app.route('/image/<int:image_id>/')
def image(image_id):
	image = Image.query.get(image_id)
	comments = image.comments
	if image==None:
		redirect('/')
	return render_template('pageDetail.html', image=image, comments=comments)

@app.route('/profile/<user_id>/')
@login_required
def profile(user_id):
	user = User.query.get(user_id)
	if user==None:
		return redirect('/')

	paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)

	return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)

@app.route('/profile/images/<user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
	paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
	map = {'has_next':paginate.has_next}

	images = []
	for image in paginate.items:
		imgvo = {'url':image.url, 'id':image.id, 'comment_count':image.comments.count()}
		images.append(imgvo)

	map['images'] = images
	return json.dumps(map)


@app.route('/regloginpage/', methods={'post', 'get'})
def regloginpage():
	msg = ''
	for m in get_flashed_messages(with_categories=False, category_filter=['reglog']):
		msg = msg + m
	return render_template('login.html', msg=msg, next=request.values.get('next'))

def redirect_with_msg(targe, msg, category):
	if msg != None:
		flash(msg, category=category)
	return redirect(targe)

@app.route('/reg/', methods={'post', 'get'})
def reg():
	username = request.values.get('username').strip()
	password = request.values.get('password').strip()

	if username=='':
		return redirect_with_msg('/regloginpage/', u'用户名不得为空', 'reglog')

	if password == '':
		return redirect_with_msg('/regloginpage/', u'密码不得为空', 'reglog')

	user = User.query.filter_by(username=username).first()

	if user != None:
		return redirect_with_msg('/regloginpage/', u'用户名已存在', 'reglog')

	m = hashlib.md5()
	salt = '.'.join(random.sample('1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJK', 10))
	m.update(password+username+salt)
	password = m.hexdigest()

	user = User(username, password, salt)
	db.session.add(user)
	db.session.commit()

	login_user(user)

	next = request.values.get('next')
	if next!=None and next.startswith('/'):
		return redirect(next)

	return redirect('/')

@app.route('/log/', methods={'post', 'get'})
def log():
	username = request.values.get('username')
	password = request.values.get('password')

	if username == '':
		return redirect_with_msg('/regloginpage/', u'用户名不得为空', 'reglog')

	if password == '':
		return redirect_with_msg('/regloginpage/', u'密码不得为空', 'reglog')

	user = User.query.filter_by(username=username).first()

	if(user == None):
		return redirect_with_msg('/regloginpage/', u'用户不存在', 'reglog')

	m = hashlib.md5()
	m.update(password+username+user.salt)

	if(user.password != m.hexdigest()):
		return redirect_with_msg('/regloginpage/', u'密码错误', 'reglog')

	login_user(user)

	next = request.values.get('next')
	print next
	if next!=None and next.startswith('/'):
		return redirect(next)

	return redirect('/')

@app.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect('/')

def save_to_local(file, filename):
	save_dir = app.config['UPLOAD_DIR']
	file.save(os.path.join(save_dir, filename))
	return '/image/'+filename

@app.route('/image/<image_name>')
def view_image(image_name):
	return send_from_directory(app.config['QINIU_DOMAIN_PREFIX'], image_name)

@app.route('/upload/', methods={"post"})
@login_required
def upload():
	print request.files
	file = request.files["file"]
	print file
	file_exp = ''
	if '.' in file.filename:
		file_exp = file.filename.rsplit('.', 1)[1].strip().lower()
	if file_exp in app.config['ALLOWED_EXTENSIONS']:
		file_name = str(uuid.uuid1()).replace('-', '')+'.'+file_exp

	#url = save_to_local(file, file_name)
	url = qiniu_uplod_file(file, file_name)

	if url != None:
		db.session.add(Image(url, current_user.id))
		db.session.commit()

	return redirect('profile/%d' %current_user.id)

@app.route('/addcomment/', methods={'post'})
def add_comment():
	image_id = int(request.values['image_id'])
	content = request.values['content']
	comment = Comment(content, current_user.id, image_id)
	db.session.add(comment)
	db.session.commit()
	return json.dumps({"code":0, "id":comment.id, "content":content,
					   "username":comment.user.username,
					   "user_id":comment.user.id})

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template("500.html"), 500