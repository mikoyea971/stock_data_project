from flask import render_template, request, redirect, url_for, flash, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..models import User, LoginLog
from ..extensions import db

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            user.last_login = datetime.utcnow()
            
            login_log = LoginLog(user_id=user.id, ip_address=request.remote_addr)
            db.session.add(login_log)
            db.session.commit()
            
            session['login_log_id'] = login_log.id
            
            flash('登录成功')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    if 'user_id' in session and 'login_log_id' in session:
        login_log = LoginLog.query.get(session['login_log_id'])
        if login_log:
            login_log.logout_time = datetime.utcnow()
            db.session.commit()
    
    session.clear()
    flash('已登出')
    return redirect(url_for('auth.login'))