#imports
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import abort
import prep as p
import datetime
from collections import defaultdict

#set up Flask and SQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '3.1415926535'
db = SQLAlchemy(app)

#SQL table class variables
class ToDos(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    task = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Exercises(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    workouts = db.relationship('Workouts', backref='exercise', lazy=True)

class Workouts(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    reps = db.Column(db.Integer, nullable=False)

    ex_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable = False)
    date_id = db.Column(db.Integer, db.ForeignKey('dates.id'), nullable = False)


class Dates(db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text, nullable=False)



#initial functions
def create_tables():
    #db.drop_all()
    db.create_all()

    if not Exercises.query.first():
        exercise1 = Exercises(name='Pushups')
        exercise2 = Exercises(name='Squat')
        exercise3 = Exercises(name='Pullups')

        db.session.add_all([exercise1, exercise2, exercise3])
        db.session.commit()
    
    print("/n/nHERE", Exercises.query.first().id)

    if not Dates.query.first():
        date1 = Dates(date='10/23')
        date2 = Dates(date='10/24')
        date3 = Dates(date='10/25')
        date4 = Dates(date='10/26')
        date5 = Dates(date='10/27')
        date6 = Dates(date='10/28')
        date7 = Dates(date='10/29')

        db.session.add_all([date1, date2, date3, date4, date5, date6, date7])
        db.session.commit()

    if not Workouts.query.first():
        workout1 = Workouts(date_id=1, reps=15, ex_id=1)
        workout2 = Workouts(date_id=2, reps=20, ex_id=2)
        workout3 = Workouts(date_id=3, reps=10, ex_id=3)

        db.session.add_all([workout1, workout2, workout3])
        db.session.commit()

    if not ToDos.query.first():
        todo1 = ToDos(title='Grocery Shopping', task='Buy milk, eggs, and bread', completed=False)
        todo2 = ToDos(title='Reading', task='Read the new novel by my favorite author', completed=True)
        todo3 = ToDos(title='Flask Project', task='Complete the Flask application for the ToDo list', completed=False)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()






#BEFORE FIRST REQUEST FUNCTION
@app.before_request
def initialize_app():
    app.before_request_funcs[None].remove(initialize_app)
    create_tables()

#main page
@app.route('/')
def index():
    #prep functions
    #posts = conn.execute('SELECT * FROM posts').fetchall()
    todos = ToDos.query.all()
    return render_template('main.html', todos=todos)

#add todo page
@app.route('/add_todo', methods=('GET', 'POST'))
def add_todo():
    if request.method == 'POST':
        title = request.form['title']
        descr = request.form['descr']

        if not title:
            flash('Title is required!')
            return redirect(url_for('add_todo'))
        else:
            new_todo = ToDos(title=title, task=descr)
            db.session.add(new_todo)
            db.session.commit()

            flash('new todo added successfully', 'success')
            return redirect(url_for('index'))
    return render_template('add_todo.html')

def load_workout(week = 0):
    exs = Exercises.query.all()
    wos = Workouts.query.all()
    week = Dates.query.all()
    
    if request.method == "POST":
        
        #handle adding new workout
        form_id = request.form.get('form_id')
        if form_id == 'form-add':
            title = request.form['new-exercise']
            if not title:
                flash('Name of exercise is required')
            else:
                new_ex = Exercises(title=title)
                db.session.add(new_ex)
                db.session.commit()
            return redirect(url_for('workout'))
        
        #handle updating database
        elif form_id == 'form-content':
            for ex in exs:
                for date in week:
                    str_find = ex.name + "-on-" + date.date
                    num = request.form.get(str_find)
                    wo = Workouts(reps=num, ex_id=ex.id, date_id=date.id)
                    db.session.add(wo)
                    db.session.commit()

            return redirect(url_for('workout'))

    return render_template('workout.html', exs = exs, wos = wos, week = week)

#workout page
@app.route('/workout', methods=('GET', 'POST'))
def workout():
    return load_workout()
    

@app.route('/workout/<int:week_id>')
def workout_week(week_id):
    return render_template('workout.html')

#post id numbers pages
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


#create page
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

#edit post pages
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

#delete page/button
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))