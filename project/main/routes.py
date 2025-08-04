from flask import render_template, redirect, url_for, session, Blueprint
from ..models import User, LoginLog

main_bp = Blueprint('main', __name__, template_folder='../templates')

@main_bp.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)
    return redirect(url_for('auth.login'))

@main_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    login_logs = LoginLog.query.filter_by(user_id=user.id).order_by(LoginLog.login_time.desc()).limit(10).all()
    
    return render_template('profile.html', user=user, login_logs=login_logs)