#imports
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import abort
import prep as p
import datetime
from datetime import date
from collections import defaultdict

#set up Flask and SQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '3.1415926535'
db = SQLAlchemy(app)

#SQL table class variables
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    task = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    workouts = db.relationship('Workout', backref='exercise', lazy=True)

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    reps = db.Column(db.Integer, nullable=False, default=0)

    ex_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable = False)
    date_id = db.Column(db.Integer, db.ForeignKey('dates.id'), nullable = False)


class Date(db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text, nullable=False)
    date_form = db.Column(db.Date, nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)

class Week(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True)
    ydl_ind = db.Column(db.Integer)

    dates = db.relationship('Date', backref='week', lazy=True)

#global variables
class Now():
    cur_day = None
    cur_week = None

now = Now()

#create weeks starting at oct
def create_weeks_from_oct():
    with app.app_context():
        ydl = p.year_dates_list
        sind = ydl.index("10/6")
        ci = 0

        for i in range(12):
            dates = []

            week_new = Week()
            db.session.add(week_new)
            db.session.commit()

            for j in range(7):
                ds = ydl[sind + ci]
                dss = ds.split("/")
                dm = int(dss[0])
                dd = int(dss[1])
                #print(dm, dd)
                df = date(2024, dm, dd)
                cd = Date(date=ds, date_form=df, week_id = week_new.id)
                dates.append(cd)
                ci += 1

            week_new.dates = dates

            db.session.add_all(dates)
            db.session.commit()


def calc_cur_week():
    with app.app_context():
        cur_date = Date.query.filter_by(date=p.today_str).first()
        cur_week = Week.query.options(joinedload(Week.dates)).filter_by(id=cur_date.week_id).first()
        return cur_date, cur_week

#initial functions
def create_tables():
    db.drop_all()
    db.create_all()

    if not Exercise.query.first():
        exercise1 = Exercise(name='Pushups')
        #exercise2 = Exercise(name='Squat')
        exercise2 = Exercise(name='Pullups')

        db.session.add_all([exercise1, exercise2])
        db.session.commit()

    """
    if not Date.query.first():
        date1 = Date(date='10/23')
        date2 = Date(date='10/24')
        date3 = Date(date='10/25')
        date4 = Date(date='10/26')
        date5 = Date(date='10/27')
        date6 = Date(date='10/28')
        date7 = Date(date='10/29')

        db.session.add_all([date1, date2, date3, date4, date5, date6, date7])
        db.session.commit()

    if not Workout.query.first():
        workout1 = Workout(date_id=1, reps=15, ex_id=1)
        workout2 = Workout(date_id=2, reps=20, ex_id=2)
        workout3 = Workout(date_id=3, reps=10, ex_id=3)

        db.session.add_all([workout1, workout2, workout3])
        db.session.commit() """

    if not ToDo.query.first():
        todo1 = ToDo(title='Grocery Shopping', task='Buy milk, eggs, and bread', completed=False)
        todo2 = ToDo(title='Reading', task='Read the new novel by my favorite author', completed=True)
        todo3 = ToDo(title='Flask Project', task='Complete the Flask application for the ToDo list', completed=False)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()


#BEFORE FIRST REQUEST FUNCTION
@app.before_request
def initialize_app():
    app.before_request_funcs[None].remove(initialize_app)
    create_tables()
    create_weeks_from_oct()
    cur_date, cur_week = calc_cur_week()
    now.cur_date = cur_date
    now.cur_week = cur_week

#main page
@app.route('/')
def index():
    #prep functions
    #posts = conn.execute('SELECT * FROM posts').fetchall()
    todos = ToDo.query.all()
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
            new_todo = ToDo(title=title, task=descr)
            db.session.add(new_todo)
            db.session.commit()

            flash('new todo added successfully', 'success')
            return redirect(url_for('index'))
    return render_template('add_todo.html')

def load_workout(week_id):
    exs = Exercise.query.all()

    #handle week variables
    if week_id == 0:
        week = now.cur_week
        week_id = week.id
    else:
        week = Week.query.filter(Week.id == week_id).first()

    if week_id - 1 >= 1:
        prev_week = Week.query.filter(Week.id == week_id - 1).first()
    else:
        print("too far back")
        prev_week = []
    
    if week_id + 1 <= 12:
        next_week = Week.query.filter(Week.id == week_id + 1).first()
    else:
        print("too far forwawrd")
        next_week = []

    start_date = week.dates[0]
    end_date = week.dates[-1]

    print("week id", week_id)
    for date in week.dates:
        print("date: ", date.date)

    print("p", prev_week)
    print("n", next_week)


    #initialize database and make sure there is a value for every workout
    for ex in exs:
        for date in week.dates:
            wo = (
            db.session.query(Workout, Exercise, Date)
            .join(Exercise, Workout.ex_id == Exercise.id)
            .join(Date, Workout.date_id == Date.id)
            .filter(Exercise.id == ex.id, Date.date == date.date)
            .first()
            )

            print("loop", ex.name, date.date, wo)

            if wo:
                wo_inst = wo[0]
                pass
                print("in data", wo[0].id, ex.name, date.date, wo[0].reps)
                print("compare", wo_inst.ex_id, ex.id, wo_inst.date_id, date.id)
            else:
                print("not in date")
                new_workout = Workout(ex_id=ex.id, date_id=date.id, reps=0)
                #print(date.date >= start_date, date.date <= end_date)
                db.session.add(new_workout)            
            wo = None

    db.session.commit()
    
    wos = (
    db.session.query(Workout, Exercise, Date)
    .join(Exercise, Workout.ex_id == Exercise.id)
    .join(Date, Workout.date_id == Date.id)
    .filter(Date.date_form >= start_date.date_form, Date.date_form <= end_date.date_form)
    .all()
    )
    print("cur len", len(wos))
            

    print("\n\nmiddle")
    for wo, e, d in wos:
        print(wo.id, e.name, d.date, wo.reps)

    if request.method == "POST":
        
        #handle adding new workout
        form_id = request.form.get('form_id')
        if form_id == 'form-add':
            title = request.form['new-exercise']
            if not title:
                flash('Name of exercise is required')
            else:
                new_ex = Exercise(name=title)
                db.session.add(new_ex)
                db.session.commit()
        
        #handle updating database
        elif form_id == 'form-content':
            for ex in exs:
                for date in week.dates:
                    print("info", ex.name, date.date)
                    

                    str_find = ex.name + "-on-" + date.date
                    num = request.form.get(str_find)

                    print("num_ori", num, type(num))
                    
                    if num != "":
                        num = int(num)
                    else:
                        num = 0

                    found = False
                    #print("/n/nstart", ex.name, date.date)
                    for wo, e, d in wos:
                        #print("test", e.name, d.date, e.id==ex.id, d.date==date.date)
                        if e.id == ex.id and d.date == date.date:
                            wo.reps = num
                            #print("in here", e.name, d.date, num)
                            found = True

                    if not found:
                        wo = Workout(ex_id=ex.id, date_id=date.id, reps=num)
                        db.session.add(wo)

                    #print(ex.name, date.date, num)
                    db.session.commit()

        #print("\n\nend")
        #for wo, e, d in wos:
        #    print(wo.id, e.name, d.date, wo.reps)
        return redirect(url_for('workout', week_id = week.id))
    #return render_template('workout.html', wos = wos, week = now.cur_week)
    return render_template('workout.html', exs = exs, wos = wos, week = week, prev_week = prev_week, next_week = next_week)

#workout page
"""
@app.route('/workout', methods=('GET', 'POST'))
def workout(week_id):
    return load_workout() """
    

@app.route('/workout/<int:week_id>', methods=('GET', 'POST'))
def workout(week_id):
    return load_workout(week_id=week_id)

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