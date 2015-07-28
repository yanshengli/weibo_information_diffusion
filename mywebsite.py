# -*- coding: utf-8 -*-
from flask import Flask, session, render_template, url_for, request, redirect, abort, _app_ctx_stack, g, flash,json
from sqlite3 import dbapi2 as sqlite3
from datetime import datetime, date
import time
# from sqlalchemy import 
# from config import POSTS_PER_PAGE

from werkzeug import check_password_hash, generate_password_hash
from hashlib import md5
import sys
import os
from build_graph_curve import build_graph_curve  
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import pymongo
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


DATABASE = 'yhfWeibo.db'
PER_PAGE = 10
DEBUG = True
SECRET_KEY = 'development key'


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


class mongodb(object):
    def __init__(self, ip, port):
        self.ip=ip
        self.port=port
        self.conn=pymongo.MongoClient(ip,port)

    def close(self):
        return self.conn.disconnect()

    def get_conn(self):
        return self.conn
conn=mongodb('219.223.245.53',27017)
data_conn=conn.get_conn()
dc=data_conn.weibo
dc.authenticate('lige', '123')

@app.route('/weibo_source',methods=['POST','GET'])
def weibo_source():
    if request.method=='POST':
       return "hello" 
    elif request.method=='GET':        
        if dc.user.find({'user_id':"1096532785"}) is None:
            pass
        else:
            datas=dc.info.find({"uid":"1096532785"})
            for data in datas:
                print data['mc']
    	    return "hello"

@app.teardown_appcontext
def close_database(exception):  
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

def get_username(user_id):
    rv = query_db('select username from user where user_id = ?',
                  [user_id], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    return 'https://secure.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)


# @app.route('/')
# def weibo():
#     if not g.user:                  # not logged in 
#         return redirect(url_for('public_info'))
#     profile_user = query_db('select * from user where username = ?',
#                             [get_username(session['user_id'])], one=True)
#     if profile_user is None:
#         abort(404)
#     following = len(query_db('''select * from follower where who_id=
#             (select user_id from user where username=? )''',
#             [g.user['username']]))
#     fans = len(query_db('''select * from follower where whom_id=
#             (select user_id from user where username=? )''',
#             [g.user['username']]))
#     num_weibo = len(query_db('''select * from message where author_id=
#             (select user_id from user where username=? )''', [g.user['username']]))
#     num_page=int(num_weibo)/10+1
#     return render_template('weibo.html', messages=query_db('''
#             select message.*, user.* from message, user
#             where message.author_id = user.user_id and (
#                 user.user_id = ? or 
#                 user.user_id in (select whom_id from follower
#                                         where who_id = ?))
#             order by message.pub_date desc limit ?''',
#             [session['user_id'], session['user_id'], PER_PAGE]), profile_user=profile_user,
#             following=following, fans=fans, num_weibo=num_weibo,page_id=1,pre_page=1,next_page=2,num_page=num_page)
#我的圈子微博翻页
@app.route('/')
@app.route('/<page_id>')
def myweibo(page_id=1):
    if not g.user:                  # not logged in 
        return redirect(url_for('public_info'))
    following = None
    fans = None
    num_weibo = None
    if int(page_id)<1:
        return redirect(url_for('myweibo'))
    if g.user:
        profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
        following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [get_username(g.user['username'])]))
        fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [get_username(g.user['username'])]))
        num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [g.user['username']]))
        if profile_user is None:
            abort(404)
    else: 
        profile_user = None
        #num_weibo=len(query_db('''select * from message '''))
    start_id=(int(page_id)-1)*10
    end_id=(int(page_id)+1)*10
    pre_page=int(page_id)-1
    next_page=int(page_id)+1
    print start_id
    print end_id
    num_page=int(num_weibo)/10+1
    if int(page_id)>num_page:return redirect(url_for('myweibo'))
    return render_template('weibo.html', messages=query_db('''
            select message.*, user.* from message, user
            where message.author_id = user.user_id and user.user_id=?
            order by message.pub_date desc limit ? ,?''',[profile_user['user_id'],start_id,PER_PAGE]),profile_user=profile_user, 
            following=following, fans=fans, num_weibo=num_weibo,pre_page=pre_page,next_page=next_page,page_id=page_id,num_page=num_page)


# @app.route('/public')
# def public_weibo():
#     following = None
#     fans = None
#     num_weibo = None
#     if g.user:
#         profile_user = query_db('select * from user where username = ?',
#                             [get_username(session['user_id'])], one=True)
#         following = len(query_db('''select * from follower where who_id=
#             (select user_id from user where username=? )''',
#             [get_username(g.user['username'])]))
#         fans = len(query_db('''select * from follower where whom_id=
#             (select user_id from user where username=? )''',
#             [get_username(g.user['username'])]))
#         num_weibo=len(query_db('''select * from message '''))
#         if profile_user is None:
#             abort(404)
#     else: 
#         profile_user = None
#         num_weibo=len(query_db('''select * from message '''))
#     num_page=int(num_weibo)/10+1
#     return render_template('weibo.html', messages=query_db('''
#             select message.*, user.* from message, user
#             where message.author_id = user.user_id
#             order by message.pub_date desc limit ? ''',[PER_PAGE]),profile_user=profile_user, 
#             following=following, fans=fans, num_weibo=num_weibo,page_id=1,pre_page=1,next_page=2,num_page=num_page)

#所有微博的翻页
@app.route('/public_weibo_info/<page_id>')
@app.route('/public_weibo_info')
def public_info(page_id=1):
    following = None
    fans = None
    num_weibo = None
    if int(page_id)<1:
        return redirect(url_for('public_info'))
    if g.user:
        profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
        following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [get_username(g.user['username'])]))
        fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [get_username(g.user['username'])]))
        num_weibo=len(query_db('''select * from message '''))
        if profile_user is None:
            abort(404)
    else: 
        profile_user = None
        num_weibo=len(query_db('''select * from message '''))
    start_id=(int(page_id)-1)*10
    end_id=(int(page_id)+1)*10
    pre_page=int(page_id)-1
    next_page=int(page_id)+1    
    num_page=int(num_weibo)/10+1
    print num_page
    if int(page_id)>num_page:return redirect(url_for('public_info'))
    return render_template('weibo.html', messages=query_db('''
            select message.*, user.* from message, user
            where message.author_id = user.user_id
            order by message.pub_date desc limit ? ,?''',[start_id,PER_PAGE]),profile_user=profile_user, 
            following=following, fans=fans, num_weibo=num_weibo,pre_page=pre_page,next_page=next_page,page_id=page_id,num_page=num_page)

#某用户微博翻页
@app.route('/people/<username>')
@app.route('/people/<username>/<page_id>')
def user_weibo(username,page_id=1):
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if  int(page_id)<1:
        return redirect(url_for('user_weibo',username=username))
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [username]))
    fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [username]))
    num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [username]))
    ####cichuyao gai
    start_id=(int(page_id)-1)*10
    pre_page=int(page_id)-1
    next_page=int(page_id)+1
    num_page=int(num_weibo)/10+1
    if int(page_id)>num_page:return redirect(url_for('user_weibo',username=username))
    return render_template('weibo.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?,?''',
            [profile_user['user_id'], start_id,PER_PAGE]), followed=followed,
            profile_user=profile_user, following=following, fans=fans, username=username, num_weibo=num_weibo,pre_page=pre_page,next_page=next_page,page_id=page_id,num_page=num_page)

################
# @app.route('/people/<username>')
# #@app.route('/people/<username>/<page_id>')
# def user_weibo(username,page_id):
#     profile_user = query_db('select * from user where username = ?',
#                             [username], one=True)
#     if profile_user is None:
#         abort(404)
#     followed = False
#     if g.user:
#         followed = query_db('''select 1 from follower where
#             follower.who_id = ? and follower.whom_id = ?''',
#             [session['user_id'], profile_user['user_id']],
#             one=True) is not None
#     following = len(query_db('''select * from follower where who_id=
#             (select user_id from user where username=? )''',
#             [username]))
#     fans = len(query_db('''select * from follower where whom_id=
#             (select user_id from user where username=? )''',
#             [username]))
#     num_weibo = len(query_db('''select * from message where author_id=
#             (select user_id from user where username=? )''', [username]))
#     ####cichuyao gai
#     return render_template('weibo.html', messages=query_db('''
#             select message.*, user.* from message, user where
#             user.user_id = message.author_id and user.user_id = ?
#             order by message.pub_date desc limit ?''',
#             [profile_user['user_id'], PER_PAGE]), followed=followed,
#             profile_user=profile_user, following=following, fans=fans, num_weibo=num_weibo)
################

#某用户微博翻页
# @app.route('/<page_id>')
# def user_weibo_more(page_id):
#     profile_user = query_db('select * from user where username = ?',
#                             [username], one=True)
#     if profile_user is None:
#         abort(404)
#     followed = False
#     if g.user:
#         followed = query_db('''select 1 from follower where
#             follower.who_id = ? and follower.whom_id = ?''',
#             [session['user_id'], profile_user['user_id']],
#             one=True) is not None
#     following = len(query_db('''select * from follower where who_id=
#             (select user_id from user where username=? )''',
#             [username]))
#     fans = len(query_db('''select * from follower where whom_id=
#             (select user_id from user where username=? )''',
#             [username]))
#     num_weibo = len(query_db('''select * from message where author_id=
#             (select user_id from user where username=? )''', [username]))
#     start_id=int(page_id)*10
#     end_id=(int(page_id)+1)*10
#     pre_page=int(page_id)-1
#     next_page=int(page_id)+1
#     print start_id
#     print end_id
#     num_page=int(num_weibo)/10+1
#     return render_template('weibo.html', messages=query_db('''
#             select message.*, user.* from message, user where
#             user.user_id = message.author_id and user.user_id = ?
#             order by message.pub_date desc limit ?,?''',
#             [profile_user['user_id'], start_id,end_id]), followed=followed,
#             profile_user=profile_user, following=following, fans=fans, num_weibo=num_weibo)

@app.route('/profile')
def profile():
    if not g.user:
        abort(401)
    profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
    if profile_user is None:
        abort(404)
    following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
    fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
    num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [g.user['username']]))
    return render_template('profile.html', profile_user=profile_user, 
            following=following, fans=fans, num_weibo=num_weibo)


@app.route('/all_user')
def all_user():
    following = fans = num_weibo = 0
    profile_user = None
    if g.user:
        profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
        following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
        fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
        num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [g.user['username']]))
    all_user = query_db('select * from user')
    if all_user is None:
        flash('目前还没有用户.')
        return redirect(url_for('public_info'))
    else:
        return render_template('users.html', all_user=all_user, profile_user=profile_user,
            following=following, fans=fans, num_weibo=num_weibo)

@app.route('/following/<username>')
def following(username):
    if not g.user:
        abort(401)
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [username]))
    fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [username]))
    num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [username]))
    myfollow_users = query_db('''select * from user where user_id=
            (select whom_id from follower where who_id=
            (select user_id from user where username=? ))''', 
            [username])
    return render_template('myfollow.html', profile_user=profile_user, 
        following=following, fans=fans, num_weibo=num_weibo, myfollow_users=myfollow_users)

@app.route('/fans/<username>')
def fans(username):
    if not g.user:
        abort(401)
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [username]))
    fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [username]))
    num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [username]))
    myfollow_users = query_db('''select * from user where user_id=
            (select who_id from follower where whom_id=
            (select user_id from user where username=? ))''', 
            [username])
    return render_template('myfollow.html', profile_user=profile_user, 
        following=following, fans=fans, num_weibo=num_weibo, myfollow_users=myfollow_users)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if not g.user:
        abort(401)
    profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
    if profile_user is None:
        abort(404)
    return render_template('profile.html', profile_user=profile_user)


@app.route('/edit', methods=['POST'])
def edit():
    if 'user_id' not in session:
        abort(401)
    if request.method == 'POST':
        if not request.form['username']:
            error = '请输入用户名'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = '请输入有效的邮箱地址.'
        elif not request.form['signature']:
            error = '请输入签名.'
        elif get_user_id(request.form['username']) is not None:
            error = '用户名已存在!'
        else:
            db = get_db()
            db.execute('''update user set username=? where user_id=?''',
                (request.form['username'], session['user_id']))
            db.execute('''update user set email=? where user_id=?''',
                (request.form['email'], session['user_id']))
            db.execute('''update user set signature=? where user_id=?''',
                (request.form['signature'], session['user_id']))
            db.commit()
            flash('您已修改资料.')
        return redirect(url_for('profile'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('myweibo'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = '请输入用户名'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = '请输入有效的邮箱地址.'
        elif not request.form['password']:
            error = '请输入密码.'
        elif request.form['password'] != request.form['password2']:
            error = '两次输入的密码不匹配.'
        elif not request.form['signature']:
            error = '请输入签名.'
        elif get_user_id(request.form['username']) is not None:
            error = '用户名已存在!'
        else:
            reg_date = str(date.today())
            db = get_db()
            db.execute('''insert into user (
              username, email, pw_hash, signature, reg_date) values (?, ?, ?, ?, ?)''',
              [request.form['username'], request.form['email'],
               generate_password_hash(request.form['password']),
               request.form['signature'], reg_date])
            db.commit()
            flash('您已成功注册.')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('myweibo'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = '用户名错误'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = '密码错误'
        else:
            flash('您已登录.')
            session['user_id'] = user['user_id']
            return redirect(url_for('myweibo'))
    return render_template('login.html', error=error)



@app.route('/logout')
def logout():
    flash('您已登出.')
    session.pop('user_id', None)
    return redirect(url_for('public_info'))


@app.route('/<username>/follow')
def follow_user(username):
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('您正在关注 "%s"' % username)
    return redirect(url_for('user_weibo', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('您已取消关注 "%s"' % username)
    return redirect(url_for('user_weibo', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, pub_date)
            values (?, ?, ?)''', (session['user_id'], request.form['text'],
            int(time.time())))
        db.commit()
        flash('已发布.')
    return redirect(url_for('myweibo'))

@app.route('/<message_id>/delete')
def delete(message_id):
    db = get_db()
    db.execute('delete from message where message_id=?', [message_id])
    db.commit()
    flash('已删除.')
    return redirect(url_for('myweibo'))

@app.route('/user_manage')
def user_manage():
    following = fans = num_weibo = 0
    profile_user = None
    if g.user:
        profile_user = query_db('select * from user where username = ?',
                            [get_username(session['user_id'])], one=True)
        following = len(query_db('''select * from follower where who_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
        fans = len(query_db('''select * from follower where whom_id=
            (select user_id from user where username=? )''',
            [g.user['username']]))
        num_weibo = len(query_db('''select * from message where author_id=
            (select user_id from user where username=? )''', [g.user['username']]))
    all_user = query_db('select * from user')
    if all_user is None:
        flash('目前还没有用户.')
        return redirect(url_for('public_info'))
    else:
        return render_template('user_manage.html', all_user=all_user, profile_user=profile_user,
            following=following, fans=fans, num_weibo=num_weibo)

@app.route('/del_user/<username>')
def del_user(username):    
    if not g.user:
        abort(401)
    if g.user['username']!="admin":
	flash(u'你无权删除，请返回', 'error')
	return redirect(url_for('all_user'))
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from user where user_id=?',[whom_id])
    db.execute('delete from message where author_id=?',[whom_id])
    db.execute('delete from follower where whom_id=?',[whom_id])
    db.commit()
    flash('您已删除 "%s"' % username)
    return redirect(url_for('all_user'))

    #return "hello"
@app.route('/show_graph')
def show_graph():
    error=None;
    node_entry,edge_entry,values,cumulative,base=build_graph_curve()
    data=list()
    data=dict(node_data=node_entry,link_data=edge_entry)
    #print data
    #node_data=json.dumps(node_data)
    #link_data=json.dumps(link_data)
    #print link_data
    return render_template('test1.html',data=data)

@app.route('/show_curve')
def show_curve():
    error=None;
    node_entry,edge_entry,values,cumulative,base=build_graph_curve()
    return render_template('show_curve.html',base=base,values=values,cumulative=cumulative)
    
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
app.jinja_env.filters['addmessage'] = add_message

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1')