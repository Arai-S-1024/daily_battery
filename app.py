from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
user_id = 0

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    current_battery = db.Column(db.Integer, server_default="100")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30), nullable = False)
    cost = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False)
    is_completed = db.Column(db.Boolean)
    is_favorite = db.Column(db.Boolean)
  
class Past_data(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(30))
    date = db.Column(db.DateTime, nullable = False)
    cost = db.Column(db.Integer, nullable = False)
    sleep_time = db.Column(db.Integer, nullable = False)
    past_battery = db.Column(db.Integer)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_data = User.query.all()
    task_list = Task.query.all()
    past_data = Past_data.query.all()

    return render_template('index.html', user_data=user_data, task_list=task_list, past_data=past_data, current_user_id=user_id)

@app.route('/create/user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        return render_template('create_user.html')
    else:
        #Userテーブル
        global user_id
        name = request.form.get('name')
        age = request.form.get('age')
        new_post = User(name=name, age=age)
        db.session.add(new_post)
        db.session.flush()
        db.session.refresh(new_post)
        user_id=new_post.id
        db.session.commit()

        return redirect('/')

@app.route('/create/task', methods=['GET','POST'])
def create_task():
    if request.method == 'GET':
        task_list = Task.query.all()
        return render_template('task.html',task_list=task_list, current_user_id=user_id)
    else:
        #taskの追加
        task_name=request.form.get('task_name')
        cost = request.form.get('cost')
        new_task_list = Task(user_id= user_id,name=task_name, cost=cost, created_at=datetime.now(), is_completed=False, is_favorite=False)
        db.session.add(new_task_list)
        db.session.commit()
        return redirect('/')

@app.route('/complete/<int:id>')
def task(id):
    task_complete = Task.query.get_or_404(id)
    task_complete.is_completed = True
    print(task_complete.user_id)
    user = User.query.get_or_404(task_complete.user_id)
    print(user)
    user.current_battery -= task_complete.cost
          
    db.session.commit()
    return redirect('/')

@app.route('/past_data/')
def past():
    return render_template('past_data.html')

@app.route('/recharge/battery')
def recharge_battery():
     user = User.query.get_or_404(user_id)
     if user.current_battery < 90:
        user.current_battery += 10
     elif user.current_battery < 100:
        user.current_battery = 100
     db.session.commit()
     return redirect('/')

@app.route('/fullcharge/battery')
def fullcharge_battery():
     user = User.query.get_or_404(user_id)
     user.current_battery = 100
     db.session.commit()
     return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)