import os
from flask import Flask
from flask import request, redirect, render_template, session
from models import db, Fcuser, Todo
from forms import RegisterForm, LoginForm
from api_v1 import api as api_v1
# app.py는 기능을 담당하는 곳

app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix='/api/v1')

@app.route('/', methods=['GET'])
def home(): # 유저아이디가 있냐 없냐에 따라서 홈페이지가 달라보여야 하므로 사용자 아이디를 전달하는 코드를 앱에다 먼저 작성한 것임
    userid = session.get('userid', None)
    todos = [] # 만약 userid가 없으면(로그인이 안됐다는 소리) todos를 전부 비워놓는 리스트를 만들고 홈페이지 안의 값들이 비워지게 됨
    if userid:
        fcuser = Fcuser.query.filter_by(userid=userid).first()
        todos = Todo.query.filter_by(fcuser_id=fcuser.id) # todo는 할일정보를 갖고 있는 api이므로 이걸 사용해서 fcuserid를 기준으로 그 사용자가 갖고있는 할일들이 홈으로 들어옴

    return render_template('home.html', userid=userid, todos=todos) # 넘기는 거 필수!!

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['userid'] = form.data.get('userid') # 로그인을 하면 세션안에 있는 쿠키에 저장되므로 세션의 userid라는 키에 폼으로부터 입력된 userid를 넣음

        return redirect('/')

    return render_template('login.html', form=form) # 폼을 안넣으면 html(보여지는 곳)에 폼기능을 전달 못하고 그 기능을 못쓰니 홈페이지에 에러가 나옴

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        fcuser = Fcuser()
        fcuser.userid = form.data.get('userid')
        fcuser.password = form.data.get('password')

        db.session.add(fcuser)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html', form=form)

basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'

# 아래의 3개 코드는 모델을 만든 다음에 진행
db.init_app(app)
db.app = app
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
