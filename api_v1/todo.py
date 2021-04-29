from flask import jsonify
from flask import request
from flask import Blueprint
from flask import session
from models import Todo, db, Fcuser
import datetime
import requests
from . import api

def send_slack(msg): # slack todos든 todos든 todos_done이든 어디서 만들어지든 간에 알림이 올수 있도록 별도의 함수를 만듦
    res = requests.post('https://hooks.slack.com/services/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', json={
        'text': msg
    }, headers={'Content-Type': 'application/json'})


@api.route('/todos/done', methods=['PUT'])
def todos_done():
    userid = session.get('userid', 1)
    if not userid:
        return jsonify(), 401

    data = request.get_json()
    todo_id = data.get('todo_id') # 할 일 자체를 불러왔을 때 가장 앞에 있는 1,2,3,4같은 이런 숫자들

    todo = Todo.query.filter_by(id=todo_id).first()
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if todo.fcuser_id != fcuser.id: # 아이디(jsoul52)값이 id(primary key)값과 다르면 실패처리를 해야됨. 본인의 할 일이 아니기 때문에
        return jsonify(), 400

    todo.status = 1 # 같다면 정삭적으로 접근했으므로 상태를 1로 바꿈 (1은 완료)

    db.session.commit()
    send_slack('TODO가 완료되었습니다\n사용자: %s\n할일 제목:%s'%(fcuser.userid, todo.title))

    return jsonify()

@api.route('/todos', methods=['GET', 'POST', 'DELETE'])
def todos():
    userid = session.get('userid', None) # 조회든 생성이든 삭제든 무조건 로그인이 돼있어야 하므로 맨위에 올림
    if not userid:
        return jsonify(), 401

    if request.method == 'POST':
        data = request.get_json() # 포스트로 전달이 들어오면 json형식으로 생성 (데이터를 어떻게 가져오는 지는 플라스크에서 이미 다 만들어 놓음)
        todo = Todo() # 모델스 파일을 보면 fcuser가 todo안의 변수로 되게끔 설정을 해놓음. 릴레이션쉽을 통해서.... 그래서 fcuser를 불러오지 않아도 됨.
        todo.title = data.get('title')

        fcuser = Fcuser.query.filter_by(userid=userid).first() # fcuser테이블 안에 있는 고유id(숫자로 된 것)값을 불러올 것이기 때문에 내가 입력한 userid를 필터로해서 그 아이디의 모든 값들을 가져옴
        todo.fcuser_id = fcuser.id # 사용자 정보에다가는 지금 로그인한 사용자를 세션으로부터 가져와서 투두 클래스변수 안에 넣었고 그걸 db세션을 통해서 데이터베이스에 저장

        todo.due = data.get('due') # 모델이나 app에 새롭게 생성이 됐으면 실질적으로 기능이 작동되는 api(여기서는 todo파일)에도 작성을 해줘야됨.
        todo.status = 0 # 모델이나 app에 새롭게 생성이 됐으면 실질적으로 기능이 작동되는 api(여기서는 todo파일)에도 작성을 해줘야됨.
        
        db.session.add(todo)
        db.session.commit()

        send_slack('TODO가 생성되었습니다\n사용자: %s\n할일 제목:%s\n기한:%s'%(fcuser.userid, todo.title, todo.due)) # 사용자 정보, 할일 제목, 기한

        return jsonify(), 201
    elif request.method == 'GET':
        todos = Todo.query.filter_by(fcuser_id=userid, status=0) # 모델스에 있는 fcuser_id가 내가 입력한 id(userid)와 같은 건 전부 다 가지고 오면 됨 
        return jsonify([t.serialize for t in todos]) # 조회기능이다 보니까 보일 때 제이슨 형태의 문자열로 보일 수 있도록 시리얼라이즈를 해준다.
    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('todo_id')

        todo = Todo.query.filter_by(id=todo_id).first()
        
        db.session.delete(todo)
        db.session.commit()

        return jsonify(), 203

    return jsonify(data)


@api.route('/slack/todos', methods=['POST'])
def slack_todos(): # slash Commands를 이용할 코드
    res = request.form['text'].split(' ')
    cmd, *args = res # 제목만 명령을 받을 것이다. ex) creat, list
                     # /flasktodo creat aaaaa를 만들거나 혹은 /flasktodo list로 만든 것을 조회 / 자세히 보면 명령의 기준이 다 띄어쓰기로 돼있음 그래서 split을 넣은거임
                     #  맨 앞에 거는 cmd로 들어가고 나머지는 *args로 들어감 

    ret_msg = '' # 리턴 메시지
    if cmd == 'create':
        todo_user_id = args[0]
        todo_name = args[1]
        todo_due = args[2]

        fcuser = Fcuser.query.filter_by(userid=todo_user_id).first()
        
        todo = Todo()
        todo.fcuser_id = fcuser.id
        todo.title = todo_name
        todo.due = todo_due
        todo.status = 0
        
        db.session.add(todo)
        db.session.commit()
        ret_msg = 'Todo가 생성되었습니다'

        send_slack('[%s] "%s" 할일을 만들었습니다.'%(str(datetime.datetime.now()), todo_name)) # 날짜및시간, 할일 제목

    elif cmd == 'list':
        todo_user_id = args[0]
        fcuser = Fcuser.query.filter_by(userid=todo_user_id).first()

        todos = Todo.query.filter_by(fcuser_id=fcuser.id)
        for todo in todos:
            ret_msg += '%d. %s (~ %s, %s)\n'%(todo.id, todo.title, todo.due, ('미완료', '완료')[todo.status])

    elif cmd == 'done':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()
        
        todo.status = 1
        db.session.commit()
        ret_msg = 'Todo가 완료 처리되었습니다'
        
    elif cmd == 'undo':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()
        
        todo.status = 0
        db.session.commit()       
        ret_msg = 'Todo가 미완료 처리되었습니다'

    return ret_msg
