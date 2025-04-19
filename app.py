from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_default_key') # required for Flask-WTF

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='Normal')
    completed = db.Column(db.Boolean, default=False)
    

class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    due_date = DateField("Due Date", format='%Y-%m-%d')
    priority = SelectField("Priority", choices=[("Low", "Low"), ("Normal", "Normal"), ("High", "High")])
    submit = SubmitField("Add Task")


@app.route("/")
def home():
    tasks = Task.query.all()
    return render_template("home.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_task.html", form=form)

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)