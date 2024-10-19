import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import prep as p
import datetime

#global variables
wos_by_ex_by_date = {}

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_data(table):
    conn = get_db_connection()
    q = 'SELECT * FROM ' + table
    table_data =  conn.execute(q).fetchall()
    return table_data

def get_normal_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_todo(todo_id):
    conn = get_db_connection()
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    conn.close()
    if todo is None:
        abort(404)
    return todo

app = Flask(__name__)
app.config['SECRET_KEY'] = '3.1415926535'

@app.before_request
def initialize_app():
    app.before_request_funcs[None].remove(initialize_app)

    #get information from db
    conn = get_db_connection()
    exs = conn.execute('SELECT * FROM exercises').fetchall()
    wos = conn.execute("SELECT * FROM workouts").fetchall()
    dates = conn.execute("SELECT * FROM dates").fetchall()
    conn.close()


    #sort wo information

    for ex in exs:
        exs_by_date = {}
        
        for date in dates:
            found = False
            for wo in wos:
                if wo["dat"] == date["str_dat"] and wo["ex"] == ex["title"] and wo["reps"] != "" and wo["reps"] != None:
                    exs_by_date[date["str_dat"]] = wo["reps"]
                    found = True
            #print("\nhi", date, found)
            if found == False:
                exs_by_date[date["str_dat"]] = 0

        wos_by_ex_by_date[ex['title']] = exs_by_date

#main page
@app.route('/')
def index():
    #prep functions
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    todos = conn.execute("SELECT * FROM todos").fetchall()
    conn.close()
    return render_template('main.html', posts=posts, todos=todos)

#add todo page
@app.route('/add_todo', methods=('GET', 'POST'))
def add_todo():
    if request.method == 'POST':
        title = request.form['title']
        descr = request.form['descr']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO todos (title, descr) VALUES (?, ?)',
                         (title, descr))
            conn.commit()
            conn.close()
    return render_template('add_todo.html')

#workout page
@app.route('/workout', methods=('GET', 'POST'))
def workout():
    #get information from db
    conn = get_db_connection()
    exs = conn.execute('SELECT * FROM exercises').fetchall()
    wos = conn.execute("SELECT * FROM workouts").fetchall()
    dates = conn.execute("SELECT * FROM dates").fetchall()
    conn.close()


    #sort wo information
    wos_by_ex_by_date = {}
    for ex in exs:
        exs_by_date = {}
        
        for date in dates:
            found = False
            for wo in wos:
                if wo["dat"] == date["str_dat"] and wo["ex"] == ex["title"] and wo["reps"] != "" and wo["reps"] != None:
                    exs_by_date[date["str_dat"]] = wo["reps"]
                    found = True
            #print("hi", date, found)
            if found == False:
                exs_by_date[date["str_dat"]] = 0

        wos_by_ex_by_date[ex['title']] = exs_by_date
    
    print(wos_by_ex_by_date) 

    if request.method == "POST":
        
        #handle adding new workout
        form_id = request.form.get('form_id')
        if form_id == 'form-add':
            title = request.form['new-exercise']
            if not title:
                flash('Name of exercise is required')
            else:
                conn = get_db_connection()
                conn.execute('INSERT INTO exercises (title) VALUES (?)',
                            (title,))
                conn.commit()
                conn.close()
            return redirect(url_for('workout'))
        
        #handle updating database
        elif form_id == 'form-content':
            conn = get_db_connection()
            exs = conn.execute('SELECT * FROM exercises').fetchall()
            dates = conn.execute("SELECT * FROM dates").fetchall()
            #print("\n\n\n SIENNA")
            for ex in exs:
                for date in dates:
                    num = request.form.get(f'{ex['title']}-on-{date['str_dat']}')
                    
                    if num != None:
                        #print("\n\n\n reps", num)
                        conn.execute('INSERT INTO workouts (ex, reps, dat) VALUES (?, ?, ?)',
                            (ex["title"], num, date['str_dat']))
                    conn.commit()

            conn.close()
            return redirect(url_for('workout'))

    return render_template('workout.html', exs = exs, wos = wos_by_ex_by_date, dates = dates)

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