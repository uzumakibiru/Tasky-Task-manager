from flask import Flask,render_template,request,flash,redirect,url_for
from flask_login import UserMixin,login_user,LoginManager,current_user,logout_user,login_required
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from flask_ckeditor import CKEditor
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, String, Text
import os
from datetime import datetime

from dotenv import load_dotenv
from forms import RegisterForm,LoginForm,TaskForm,Add,ProjectForm
current_year=datetime.now().year
task_list=[]
project_name=""

load_dotenv()
app=Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASH_KEY")
ckeditor=CKEditor(app)
Bootstrap5(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
#COnfigure flask_login
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)
#Create Database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DB_URI",'sqlite:///taskmanager.db')
db=SQLAlchemy(model_class=Base)
db.init_app(app)

#Configure Table for registered user
class User(UserMixin,db.Model):
    __tablename__="users"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    email:Mapped[str]=mapped_column(String(100),unique=True)
    password:Mapped[str]=mapped_column(String(100))
    name:Mapped[str]=mapped_column(String(100))
#Table for the personal tod0 list
class Task(db.Model):
    __tablename__="tasks"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user:Mapped[str]=mapped_column(String(100))
    todo:Mapped[str]=mapped_column(String(1000))
#Ttable to assign user for a project
class Adduser(db.Model):
    __tablename__="addusers"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    team:Mapped[str]=mapped_column(String(100))
#Table for the grouo task
class Project(db.Model):
    __tablename__="projects"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    team:Mapped[str]=mapped_column(String(100))
    project:Mapped[str]=mapped_column(String)
#Table for the group task to complete
class Complete(db.Model):
    __tablename__="completes"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    team:Mapped[str]=mapped_column(String(100))
    completed_task:Mapped[str]=mapped_column(String)
#Table for Project name
class Pname(db.Model):
    __tablename__="pnames"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    
    project_name:Mapped[str]=mapped_column(String)
with app.app_context():
    db.create_all()
#Home page
@app.route("/")
def home():
    return render_template("index.html",current_user=current_user,current_year=current_year)
@app.route("/register",methods=["POST","GET"])
#Register new user page
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        #CHeck the user have already signed up
        result=db.session.execute(db.select(User).where(User.email==form.email.data))
        user=result.scalar()
        #User exist then user is True
        if user:
            flash("Email already in use. Please Log in.")
            return redirect(url_for('login'))
        hash_salt_password=generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user=User(
            email=form.email.data,
            name=form.name.data,
            password=hash_salt_password,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home',current_user=current_user,current_year=current_year))

    return render_template("register.html",form=form)
#Login page
@app.route("/login",methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        password=form.password.data
        result=db.session.execute(db.select(User).where(User.email==form.email.data))
        user= result.scalar()

        if not user:
            flash("Incorrect Email address.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password,password):
            flash("Incorrect Password.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home',current_user=current_user))
    


    return render_template("login.html",form=form,current_user=current_user,current_year=current_year)
#Personal to do page
@app.route("/task",methods=["POST","GET"])
def task():
    form=TaskForm()
    if form.validate_on_submit():
        
        task=form.task.data
        new_task=Task(
            todo=task,
            user=current_user.email
        )
        db.session.add(new_task)
        db.session.commit()
        form.task.data=''
    if current_user.is_authenticated:
        result=db.session.execute(db.select(Task).where(Task.user==current_user.email))
        tasks=result.scalars().all()
        return render_template("task.html",form=form,tasks=tasks,current_user=current_user,current_year=current_year)
    
    return render_template("task.html",form=form,current_user=current_user,current_year=current_year)
#Delete personal task
@app.route("/delete",methods=["POST"])
def delete_task():
    tasks_ids=request.form.getlist('tasks_ids')

    
    for task_id in tasks_ids:
        task=db.session.execute(db.select(Task).where(Task.id==task_id)).scalar()
        
        if task:
            db.session.delete(task)
        db.session.commit()
    return redirect(url_for('task',current_year=current_year))
#Project Page
@app.route("/project",methods=["POST","GET"])
def project():
    userform=Add()
    form=ProjectForm()
    teams=db.session.execute(db.select(Adduser))
    team=teams.scalars().all()
    results=[]
    results=db.session.execute(db.select(User)).scalars().all()
    #Project name
    project_names=db.session.execute(db.select(Pname))
    project_name=project_names.scalar()
    #All the assigned task
    post_result=db.session.execute(db.select(Project))
    tasks=post_result.scalars().all()
    #All the complted atsk
    complete_task=db.session.execute(db.select(Complete))
    complete_tasks=complete_task.scalars().all()
    #All the users
    
    teams=db.session.execute(db.select(Adduser))
    team=teams.scalars().all()
    
        #Return statement required otherwise CSRF token error
        # return render_template("project.html",current_user=current_user,userform=userform,form=form,team=team,results=results)
    if form.validate_on_submit():
        task=form.task.data
        new_task=Project(
            project=task,
            team=current_user.email
        )
        db.session.add(new_task)
        db.session.commit()
        form.task.data=''
    post_result=db.session.execute(db.select(Project))
    tasks=post_result.scalars().all()
    if current_user.is_authenticated:
        add_user=db.session.execute(db.select(Adduser).where(Adduser.team==current_user.email))
        add_users=add_user.scalar()
        return render_template("project.html",gravatar=gravatar,current_user=current_user,userform=userform,form=form,team=team,results=results,add_users=add_users,tasks=tasks,current_year=current_year,complete_tasks=complete_tasks,project_name=project_name)
    
   
        # return render_template("project.html",current_user=current_user,userform=userform,form=form,team=team,results=results,add_users=add_users,tasks=tasks)
    return render_template("project.html",gravatar=gravatar,current_user=current_user,userform=userform,form=form,team=team,results=results,tasks=tasks,current_year=current_year,complete_tasks=complete_tasks,project_name=project_name)

#Assigning task to the user by transferring from one table to another
@app.route("/delete_project_task",methods=["POST"])
def delete_project_task():
    tasks_ids=request.form.getlist('tasks_ids')
    for task_id in tasks_ids:
        task=db.session.execute(db.select(Project).where(Project.id==task_id)).scalar()
        new_task=Complete(
            completed_task=task.project,
            team=current_user.email
        )
        db.session.add(new_task)
        db.session.commit()
    for task_id in tasks_ids:
        task=db.session.execute(db.select(Project).where(Project.id==task_id)).scalar()
        # task_list.append(task)
        if task:
            db.session.delete(task)
        db.session.commit()
    return redirect(url_for('project'))
#Delete the entire project
@app.route("/delete_project")
def delete_project():
    #Delete Project name
    results=db.session.execute(db.select(Pname)).scalars().all()
    for result in results:
        if result:
            db.session.delete(result)
        db.session.commit()
    #Delete Complteed task
    results=db.session.execute(db.select(Complete)).scalars().all()
    for result in results:
        if result:
            db.session.delete(result)
        db.session.commit()
    #Delete Project team
    results=db.session.execute(db.select(Adduser)).scalars().all()
    for result in results:
        if result:
            db.session.delete(result)
        db.session.commit()
    #Delete the Project task
    results_project_task=db.session.execute(db.select(Project)).scalars().all()
    for item in results_project_task:
        if result:
            db.session.delete(item)
        db.session.commit()
    return redirect(url_for('project'))
#about page
@app.route("/about")
def about():
    return render_template("about.html",current_year=current_year)   

#Add user to the group task/project
@app.route("/add",methods=["POST"])
def add():
    if request.method=="POST":
        query_email=request.form.getlist("user_id")
        project_name=request.form.get('project_name')
        add_name=Pname(
                project_name=project_name
                )
        db.session.add(add_name)
        db.session.commit()
        for em in query_email:
                add_team=Adduser(
                team=em
                )
                db.session.add(add_team)
        db.session.commit()
        # teams=db.session.execute(db.select(Adduser))
        # team=teams.scalars().all()
        return render_template("add.html",current_year=current_year)  
#Logout feature   
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=False)