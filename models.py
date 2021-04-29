from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Todo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    fcuser_id = db.Column(db.Integer, db.ForeignKey('fcuser.id'), nullable=False) # todo에 사용자 아이디를 연결해줌
    title = db.Column(db.String(256))
    status = db.Column(db.Integer)
    due = db.Column(db.String(64))
    tstamp = db.Column(db.DateTime, server_default=db.func.now()) # 현재시간이 들어가도록 함

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'fcuser': self.fcuser.userid,
            'tstamp': self.tstamp
        }


class Fcuser(db.Model):
    __tablename__ = 'fcuser'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32))
    password = db.Column(db.String(128))
    todos = db.relationship('Todo', backref='fcuser', lazy=True) # 다른 모델(todo)에서 나(fcuser)를 데려갈 때 fcuser를  다른 모델의 변수(todo)에 (fcuser)를 등록해주겠다
                                                                 # lazy가 트루인 것은 데이터베이스에서 가지고 올때 로드를 해주겠다
