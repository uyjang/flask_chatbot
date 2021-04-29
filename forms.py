from models import Fcuser
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    repassword = PasswordField('repassword', validators=[DataRequired()])

class LoginForm(FlaskForm):

    class UserPassword(object): # 비밀번호가 맞는 지 확인하는 밸리데이터 클래스
        def __init__(self, message=None): # 여기서 메시지는 틀렸을 때 나오는 메시지
            self.message = message
            
        def __call__(self, form, field): # 이 함수가 실행되면서 폼이랑 필드가 같이 넘어옴
            userid = form['userid'].data
            password = field.data

            fcuser = Fcuser.query.filter_by(userid=userid).first() # 해당 유저아이디를 가지고 있는 사람은 한명밖에 없을 테니 first만 써도 충분함
            if fcuser.password != password: # fcuser에서 비밀번호를 가지고 오고 내가 지금 입력한 비밀번호랑 비교를 해서 맞는 지 확인함
                raise ValueError('Wrong password')

    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()]) # 데이터가 있을 때 그 비밀번호가 맞는 지 확인해야 하니 데이터리콰이어 뒤에 오고 패스워드 벨리데이터 속성에 넣음
