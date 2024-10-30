#imports
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_assets import Environment, Bundle
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

# Set up Flask-Assets
assets = Environment(app)

# Define SCSS Bundle
scss_bundle_base = Bundle(
    'scss/base.scss',
    filters='libsass',
    output='css/base.css'  # Compiled CSS output for base.html
)

scss_bundle_todo_main = Bundle(
    'scss/todo_main.scss',
    filters='libsass',
    output='css/todo_main.css'  # Compiled CSS output for todo_main.html
)

scss_bundle_add_todo = Bundle(
    'scss/add_todo.scss',
    filters='libsass',
    output='css/add_todo.css'  # Compiled CSS output for add_todo.html
)

scss_bundle_workout = Bundle(
    'scss/workout.scss',
    filters='libsass',
    output='css/workout.css'  # Compiled CSS output for workout.html
)

# Register each bundle with a unique name
assets.register('base_css', scss_bundle_base)
assets.register('todo_main_css', scss_bundle_todo_main)
assets.register('add_todo_css', scss_bundle_add_todo)
assets.register('workout_css', scss_bundle_workout)


#---------SQL table class variables----------
class ToDo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    comp = db.Column(db.Boolean, default=False)
    pri = db.Column(db.Integer, nullable=False)
    
    #date stuff
    date_e = db.Column(db.Text, nullable=False)
    date_e_form = db.Column(db.Date, nullable=False)
    date_d = db.Column(db.Text, nullable=False)
    date_d_form = db.Column(db.Date, nullable=False)
    

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

def date_str_to_form(ds):
    dss = ds.split("/")
    dm = int(dss[0])
    dd = int(dss[1])
    df = date(2024, dm, dd)
    return df


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
        exercise2 = Exercise(name='Pullups')

        db.session.add_all([exercise1, exercise2])
        db.session.commit()

    if not ToDo.query.first():
        todo1 = ToDo(title='Flask Project', desc='Complete the Flask application for the ToDo list', comp=False, pri=0, date_e="10/25", date_e_form=date_str_to_form("10/25"), date_d="12/31", date_d_form=date_str_to_form("12/31"))

        db.session.add(todo1)
        db.session.commit()

#----PAGE FUNCTIONS---------
def load_workout(week_id):
    exs = Exercise.query.all()

    #handle week variables
    if week_id == 0:
        week = now.cur_week
        print(week)
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

def load_todo():
    todos = ToDo.query.all()

    if request.method == "POST":
        #get information
        title = request.form['new-todo-title-input']
        desc = request.form['new-todo-desc-input']
        due = request.form['new-todo-due-input']
        pri = request.form['new-todo-pri-input']

        #calculate information
        dd_f = date_str_to_form(due)
        date_e = p.today_str
        de_f = date_str_to_form(date_e)

        #add new todo
        new_todo = ToDo(title=title, desc=desc, comp=False, pri=pri, date_e=date_e, date_e_form=de_f, date_d=due, date_d_form=dd_f)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('todo'))

    return render_template('todo_main.html', todos = todos)

#BEFORE FIRST REQUEST FUNCTION
@app.before_request
def initialize_app():
    #print("init")
    app.before_request_funcs[None].remove(initialize_app)
    create_tables()
    create_weeks_from_oct()
    cur_date, cur_week = calc_cur_week()
    now.cur_date = cur_date
    now.cur_week = cur_week

#----------PAGES------------------

#main page
@app.route('/')
def index():
    todos = ToDo.query.all()
    return render_template('main.html', todos=todos)

#workout page
@app.route('/workout/<int:week_id>', methods=('GET', 'POST'))
def workout(week_id):
    return load_workout(week_id=week_id)

#todo page
@app.route('/todo', methods=('GET', 'POST'))
def todo():
    return load_todo()

