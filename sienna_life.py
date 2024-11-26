#----------------------SET UP------------------------------------------------------

#imports
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
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

scss_bundle_routine = Bundle(
    'scss/routine.scss',
    filters='libsass',
    output='css/routine.css'  # Compiled CSS output for workout.html
)

# Register each bundle with a unique name
assets.register('base_css', scss_bundle_base)
assets.register('todo_main_css', scss_bundle_todo_main)
assets.register('add_todo_css', scss_bundle_add_todo)
assets.register('workout_css', scss_bundle_workout)
assets.register('routine_css', scss_bundle_routine)


#-------------SQL table class variables---------------------------

#todo page
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

    days_so_far = db.Column(db.Integer, nullable = False, default=0)
    days_left = db.Column(db.Integer, nullable = False, default=0)

    #category stuff
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, default=1)
    cat_name = db.Column(db.Text)

    def calc_days(self):
        diff_sf = date_str_to_form(p.today_str) - date_str_to_form(self.date_e)
        self.days_so_far = diff_sf.days

        if self.comp:
            self.days_left = 0 
        else:
            diff_l = date_str_to_form(self.date_d) - date_str_to_form(p.today_str)
            self.days_left = diff_l.days

        #print("\n\n", self.days_so_far, self.days_left)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    todos = db.relationship('ToDo', backref='categories', lazy=True)        
    
#workout page
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

#date and time stuff
class Date(db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text, nullable=False)
    date_form = db.Column(db.Date, nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)

class Week(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True)
    dates = db.relationship('Date', backref='week', lazy=True)


#routine stuff
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)

    cat_id = db.Column(db.Integer, db.ForeignKey('task_categories.id'), nullable=False, default=1)
    cat_name = db.Column(db.Text)
    records = db.relationship('TaskRecord', backref='task', lazy=True)

class TaskRecord(db.Model):
    __tablename__ = 'task_records'
    id = db.Column(db.Integer, primary_key=True)
    comp = db.Column(db.Boolean, default=False)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    date_id = db.Column(db.Integer, db.ForeignKey('dates.id'), nullable=False)

class TaskCategory(db.Model):
    __tablename__ = 'task_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    tasks = db.relationship('Task', backref='task_categories', lazy=True)

class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


#--------------------- PREPARATION -----------------------------------------

#global variables
class Now():
    cur_day = None
    cur_week = None

now = Now()

def calc_cur_week():
    with app.app_context():
        #print(p.today_str)
        cur_date = Date.query.filter_by(date=p.today_str).first()
        cur_week = Week.query.options(joinedload(Week.dates)).filter_by(id=cur_date.week_id).first()
        return cur_date, cur_week
    
calc_cur_week()
    
def date_str_to_form(ds):
    dss = ds.split("/")
    dm = int(dss[0])
    dd = int(dss[1])
    df = date(2024, dm, dd)
    return df


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


#old create tables for exercises
#DO NOT USE WILL DELETE DATA
def create_tables_ex_old():
    db.drop_all()
    db.create_all()

    if not Exercise.query.first():
        exercise1 = Exercise(name='Pushups')
        exercise2 = Exercise(name='Pullups')

        db.session.add_all([exercise1, exercise2])
        db.session.commit()

def create_todo_ex():

    if not Category.query.first():
        cat1 = Category(name='Random')
        db.session.add(cat1)
        db.session.commit()

    if not ToDo.query.first():
        cat1 = Category.query.first()
        todo1 = ToDo(title='Flask Project', desc='Complete the Flask application for the ToDo list', comp=False, pri=0, date_e="10/25", date_e_form=date_str_to_form("10/25"), date_d="12/31", date_d_form=date_str_to_form("12/31"), cat_id = cat1.id)

        db.session.add(todo1)
        db.session.commit()

def reset_db():
    db.drop_all()
    db.create_all()

def clear_table(model):
    model.query.delete()
    db.session.commit()

def calc_prev_and_next_weeks(week_id):
    if week_id - 1 >= 1:
        prev_week = Week.query.filter(Week.id == week_id - 1).first()
    else:
        #print("too far back")
        prev_week = []
    
    if week_id + 1 <= 12:
        next_week = Week.query.filter(Week.id == week_id + 1).first()
    else:
        #("too far forwawrd")
        next_week = []
    return prev_week, next_week
    



#------------------PAGE FUNCTIONS-----------------------------------------
def load_workout(week_id):
    exs = Exercise.query.all()

    #handle week variables
    if week_id == 0:
        week = now.cur_week
        #print(week)
        week_id = week.id
    else:
        week = Week.query.filter(Week.id == week_id).first()

    prev_week, next_week = calc_prev_and_next_weeks(week_id)

    start_date = week.dates[0]
    end_date = week.dates[-1]

    #print("week id", week_id)
    #for date in week.dates:
    #    print("date: ", date.date)

    #print("p", prev_week)
    #print("n", next_week)


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

            #print("loop", ex.name, date.date, wo)

            if wo:
                wo_inst = wo[0]
                pass
                #print("in data", wo[0].id, ex.name, date.date, wo[0].reps)
                #print("compare", wo_inst.ex_id, ex.id, wo_inst.date_id, date.id)
            else:
                #print("not in date")
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
    #print("cur len", len(wos))
            

    #print("\n\nmiddle")
    for wo, e, d in wos:
        #print(wo.id, e.name, d.date, wo.reps)
        pass

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
                    #print("info", ex.name, date.date)
                    

                    str_find = ex.name + "-on-" + date.date
                    num = request.form.get(str_find)

                    #print("num_ori", num, type(num))
                    
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

def todo_form_handling(request, cats):

    form_id = request.form['form_id']
    #print("fi", form_id)

    if form_id == 'todo-add':
        #get information
        title = request.form['new-todo-title-input']
        desc = request.form['new-todo-desc-input']
        due = request.form['new-todo-due-input']
        pri = request.form['new-todo-pri-input']
        cat_name = request.form['new-todo-cat-input']
        #print("CAT", cat)

        #calculate date information
        dd_f = date_str_to_form(due)
        date_e = p.today_str
        de_f = date_str_to_form(date_e)

        #calculate category information
        cat = Category.query.filter_by(name=cat_name).first()
        cat_id = cat.id if cat else None

        #add new todo
        new_todo = ToDo(title=title, desc=desc, comp=False, pri=pri, date_e=date_e, date_e_form=de_f, date_d=due, date_d_form=dd_f, cat_id=cat_id, cat_name=cat_name)
        db.session.add(new_todo)
        db.session.commit()

    elif form_id == "cat-add":
        name = request.form['new-cat-input']
        #print("\nADDING: ", name)
        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()

    return redirect(url_for('todo'))

def load_todo():
    todos = ToDo.query.all()
    cats = Category.query.all()

    if request.method == "POST":
        return todo_form_handling(request, cats)

    #put a category for each todo
    for todo in todos:
        todo.calc_days()
        for cat in cats:
            if cat.id == todo.cat_id:
                todo.cat_name = cat.name

    todos = ToDo.query.all()
    cats = Category.query.all()
        
    return render_template('todo_main.html', todos = todos, cats=cats)

def load_todo_sort(sort_cat, order):
    todos = ToDo.query.all()
    cats = Category.query.all()

    if request.method == "POST":
        return todo_form_handling(request, cats)

    #sort the sort category
    if sort_cat == "category":
        sort_attr = ToDo.cat_name
    elif sort_cat == "name":
        sort_attr = ToDo.title
    elif sort_cat == "due_date":
        sort_attr = ToDo.date_d_form
    elif sort_cat == "days_so_far":
        sort_attr = ToDo.days_so_far
    elif sort_cat == "days_left":
        sort_attr = ToDo.days_left
    elif sort_cat == "priority":
        sort_attr = ToDo.pri

    todos_sorted = (
        ToDo.query
        .join(Category)
        .order_by(sort_attr, ToDo.date_d_form)
        .all()
    )

    if order=="down":
        todos_sorted.reverse()

    print("\n\n\n type:", type(todos_sorted))

    print("\n\n\n list")
    for todo in todos_sorted:
        print(todo.id)

    return render_template('todo_main.html', todos = todos_sorted, cats=cats)


def routine_form_handling(cats):
    form_id = request.form['form_id']

    if form_id == "cat-add":
        name = request.form['new-cat-input']
        new_cat = TaskCategory(name=name)
        db.session.add(new_cat)
        db.session.commit()

    elif form_id == 'task-add':
        name = request.form['task-name']
        desc = request.form['task-desc']
        cat_name = request.form['add-cat-select']

        for cat in cats:
            if cat.name == cat_name:
                cat_id = cat.id

        new_task = Task(name=name, desc=desc, cat_id = cat_id, cat_name=cat_name)
        db.session.add(new_task)
        db.session.commit()
    
    return redirect(url_for('routine', week_id = 0))

def routine_make_recs(week):
    tasks = Task.query.all()
    task_records = TaskRecord.query.all()
    cats = TaskCategory.query.all()

    for task in tasks:
        for date in week.dates:
            rec = (
                db.session.query(TaskRecord, Task, Date)
                .join(Task, TaskRecord.task_id == Task.id)
                .join(Date, TaskRecord.date_id == Date.id)
                .filter(Task.id == task.id, Date.id == date.id)
                .first()
            )

            if not rec:
                new_rec = TaskRecord(task_id = task.id, date_id = date.id, comp = False)
                db.session.add(new_rec)

            rec = None
    db.session.commit()

def day_calc_comp(date, tasks):
    tot = 0
    done = 0
    for task in tasks:
        tot += 1
        task_record = TaskRecord.query.filter_by(task_id=task.id, date_id=date.id).first()
        if task_record.comp == True:
            done += 1
    
    if tot!=0:
        comp = round(round(done/tot, 2) * 100)
    else:
        comp = 0
    return comp

def routine_calc_comp(week, tasks):
    
    comps = []
    for date in week.dates:
        tot = 0
        done = 0
        for task in tasks:
            tot += 1
            task_record = TaskRecord.query.filter_by(task_id=task.id, date_id=date.id).first()
            if task_record.comp == True:
                done += 1

        if tot!= 0:
            comp = round(round(done/tot, 2) * 100)
        else:
            comp = 0
        comps.append( (date, comp) )
    return comps

def find_week_from_date(week_id, date_id):
    date = Date.query.get(date_id)
    if date:
        return date.week_id
    else:
        return None

        

def load_routine(week_id):
    if week_id == 0:
        week = now.cur_week
        week_id = week.id
    else:
        week = Week.query.filter(Week.id == week_id).first()

    prev_week, next_week = calc_prev_and_next_weeks(week_id)

    tasks = Task.query.all()
    task_records = TaskRecord.query.all()
    cats = TaskCategory.query.all()

    start_date = week.dates[0]
    end_date = week.dates[-1]

    routine_make_recs(week)
    comps = routine_calc_comp(week, tasks)

    #continue here
    recs = (
    db.session.query(TaskRecord, Task, Date)
    .join(Task, TaskRecord.task_id == Task.id)
    .join(Date, TaskRecord.date_id == Date.id)
    .filter(Date.date_form >= start_date.date_form, Date.date_form <= end_date.date_form)
    .all()
    )

    if request.method == "POST":
        return routine_form_handling(cats)

    tasks = Task.query.all()
    task_records = TaskRecord.query.all()
    cats = TaskCategory.query.all()

    return render_template('routine_main.html', ts = tasks, week = week, recs = recs, cats=cats, comps=comps)


#BEFORE FIRST REQUEST FUNCTION
@app.before_request
def initialize_app():
    #print("init")
    app.before_request_funcs[None].remove(initialize_app)
    #clear_table(ToDo)
    #clear_table(Category)
    #clear_table(Task)
    #clear_table(TaskCategory)
    #reset_db()
    create_weeks_from_oct()
    cur_date, cur_week = calc_cur_week()
    now.cur_date = cur_date
    now.cur_week = cur_week

#---------------------PAGES-----------------------------------

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

#todo page sort
@app.route('/todo/sort/<string:sort_cat>/<string:order>', methods=('GET', 'POST'))
def todo_sort(sort_cat, order):
    return load_todo_sort(sort_cat, order)

#todo checkbox ajax
@app.route('/update-todo-checkbox', methods=["POST"])
def update_todo_checkbox():

    data=request.get_json()
    todo_id = data['todo_id']
    is_checked = data['checked']

    todo = ToDo.query.get(todo_id)
    if todo:
        todo.comp = is_checked
        todo.calc_days()
        db.session.commit()

        return jsonify({
            "success": True,
            "todo_id": todo_id, 
            "checked": is_checked,
            "days_left": todo.days_left}), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Todo not found'
        }), 404
    

#routine page
@app.route('/routine/<int:week_id>', methods=('GET', 'POST'))
def routine(week_id):
    return load_routine(week_id=week_id)

#todo checkbox ajax
@app.route('/update-task-checkbox', methods=["POST"])
def update_task_checkbox():

    data=request.get_json()
    task_id = data['task_id']
    date_id = data['date_id']
    is_checked = data['checked']

    date = Date.query.get(date_id)

    tasks = Task.query.all()
    
    

    task_record = TaskRecord.query.filter_by(task_id=task_id, date_id=date_id).first()
    if task_record:

        task_record.comp = is_checked
        db.session.commit()
        comp = day_calc_comp(date, tasks)

        return jsonify({
            "success": True,
            "todo_id": task_id, 
            "checked": is_checked,
            "comp": comp}), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Todo not found'
        }), 404


#delete task
@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = request.json.get('task_id')
    task = Task.query.get(task_id)

    if task:
        TaskRecord.query.filter_by(task_id=task_id).delete()
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success":True, "message": f"Task {task_id} deleted."})
    else:
        return jsonify({"success": False, "message": "Task not found."}), 404


