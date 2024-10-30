#------IMPORTS AND SET UP------
import os
from flask import Flask
from flask import render_template,url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_required,current_user,login_user,logout_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import InputRequired,Length,DataRequired,NumberRange
import hashlib
from functools import wraps
from flask import abort
from werkzeug.utils import secure_filename
import secrets
from PIL import Image
from datetime import datetime,timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
print(app.config['SQLALCHEMY_DATABASE_URI'])
db=SQLAlchemy(app)
app.config['SECRET_KEY']='sweetesthoney'
app.config['UPLOAD_FOLDER'] = 'static/uploads'


login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="userlogin"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def librarian_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != 'librarian':
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return decorated_view




#------MODELS------
class User(db.Model, UserMixin):
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    role=db.Column(db.String, nullable=False)

    def get_id(self):
        return str(self.user_id)
    
class Book(db.Model,UserMixin):
    book_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    bookname=db.Column(db.String, nullable=False, unique=True)
    file_path=db.Column(db.String,nullable=False)
    author=db.Column(db.String,nullable=False)
    description=db.Column(db.String, nullable=False)
    image=db.Column(db.String, nullable=False)
    date=db.Column(db.DateTime,nullable=False)

class User_Book(db.Model, UserMixin):
    uid=db.Column(db.Integer, primary_key=True, nullable=False)
    bid=db.Column(db.Integer, primary_key=True, nullable=False)
    u_name=db.Column(db.Integer,nullable=False)
    b_name=db.Column(db.String, nullable=False)
    status=db.Column(db.String,nullable=False)
    date_received=db.Column(db.DateTime)

class Section(db.Model,UserMixin):
    section_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    section_name=db.Column(db.String, nullable=False, unique=True)
    s_description=db.Column(db.String, nullable=False)
    s_image=db.Column(db.String, nullable=False)
    s_date=db.Column(db.DateTime,nullable=False)

class Section_Book(db.Model,UserMixin):
    sec_id=db.Column(db.Integer, primary_key=True, nullable=False)
    b_id=db.Column(db.Integer, primary_key=True, nullable=False)

class Feedback(db.Model,UserMixin):
    u_id=db.Column(db.Integer, primary_key=True, nullable=False)
    b_id=db.Column(db.Integer, primary_key=True, nullable=False)
    uname=db.Column(db.Integer,nullable=False)
    bname=db.Column(db.String, nullable=False)
    feedback=db.Column(db.String,nullable=False)

class User_Notes(db.Model,UserMixin):
    n_id=db.Column(db.Integer,primary_key=True,nullable=False)
    id_u=db.Column(db.Integer,primary_key=True,nullable=False)
    notes=db.Column(db.String,nullable=False)


#------FORMS------
class RegisterForm(FlaskForm):
    username=StringField(validators=[
        InputRequired(), Length(min=5, max=18)], render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[
        InputRequired(), Length(min=5, max=18)], render_kw={"placeholder":"Password"})
    submit=SubmitField("Register")

class LoginForm(FlaskForm):
    username=StringField(validators=[
        InputRequired(), Length(min=5, max=18)], render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[
        InputRequired(), Length(min=5, max=18)], render_kw={"placeholder":"Password"})
    submit=SubmitField("Login")

class BookForm(FlaskForm):
    bookname=StringField('Book name',validators=[
        InputRequired()], render_kw={"placeholder":"Book name"})
    book=FileField('Upload Content',validators=[FileAllowed(['pdf'], 'Only PDF files allowed!'),
        FileRequired()
    ])
    author=StringField(validators=[
        InputRequired()], render_kw={"placeholder":"Author name"})
    description=TextAreaField(validators=[
        InputRequired()],render_kw={"placeholder": "Description"})
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'])], render_kw={"placeholder": "Picture"})
    submit=SubmitField("Submit")

class EditBookForm(FlaskForm):
    book=FileField('Upload Content',validators=[FileAllowed(['pdf'], 'Only PDF files allowed!')
    ])
    author=StringField(render_kw={"placeholder":"Author name"})
    description=TextAreaField(render_kw={"placeholder": "Description"})
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'])], render_kw={"placeholder": "Picture"})
    submit=SubmitField("Edit Book")

class SectionForm(FlaskForm):
    section_name=StringField('Section name',validators=[
        InputRequired()], render_kw={"placeholder":"Section name"})
    s_description=TextAreaField('Description',validators=[
        InputRequired()],render_kw={"placeholder": "Description"})
    s_image=FileField('Image',validators=[FileAllowed(['jpg', 'png', 'jpeg'])], render_kw={"placeholder": "Picture"})
    submit=SubmitField("Submit Section")

class EditsectionForm(FlaskForm):
    s_description=TextAreaField('Description',render_kw={"placeholder": "Description"})
    s_image=FileField('Image',validators=[FileAllowed(['jpg', 'png', 'jpeg'])], render_kw={"placeholder": "Picture"})
    submit=SubmitField("Edit Section")

class SearchForm(FlaskForm):
    search=StringField(render_kw={"placeholder": "Search"})
    submit=SubmitField("Search")

class ReturnForm(FlaskForm):
    submit=SubmitField("Return")

class RequestForm(FlaskForm):
    submit=SubmitField("Request")

class GrantForm(FlaskForm):
    submit=SubmitField("Grant")

class RejectForm(FlaskForm):
    submit=SubmitField("Reject")

class CancelreqForm(FlaskForm):
    submit=SubmitField("Cancel Request")

class RevokeForm(FlaskForm):
    submit=SubmitField("Revoke")

class AddbookForm(FlaskForm):
    b_section=SelectField('Select a Section', coerce=int, validators=[DataRequired()])
    submit=SubmitField('Add Book')

class FeedbackForm(FlaskForm):
    feedback=TextAreaField('Give Feedback',validators=[
        InputRequired()],render_kw={"placeholder": "Type Here"})
    submit=SubmitField('Submit')

class NotesForm(FlaskForm):
    notes=TextAreaField('Notes',validators=[
        InputRequired()],render_kw={"placeholder": "Add a notes"})
    submit=SubmitField('Submit')

#------CONTROLLERS------  
    
@app.route("/")
def home():
    return render_template("home.html")

def hash(a):
    hashed=hashlib.sha256(str.encode(a)).hexdigest()
    return hashed


@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(username=form.username.data).first():
            hashed_password = hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password, role="user")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('welcome'))
    return render_template("registration.html", form=form)

@app.route("/userlogin",methods=["GET","POST"])
def userlogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if hash(form.password.data) == user.password and user.role == "user":
                login_user(user)
                return redirect(url_for("userfeed",user_id=user.user_id))
    return render_template("userlogin.html", form=form)

@app.route("/librarian-login",methods=["GET","POST"])
def librarianlogin():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if form.password.data==user.password and user.role=="librarian":
                login_user(user)
                return redirect(url_for('librarianfeed'))
    return render_template('librarianlogin.html', form=form)

@app.route("/userfeed/<int:user_id>", methods=["GET","POST"])
@login_required
def userfeed(user_id):
    s_form=SearchForm()
    if s_form.validate_on_submit():
        return redirect(url_for('search_book',q=s_form.search.data))
    books = Book.query.order_by(Book.book_id.desc()).all()
    sections=Section.query.order_by(Section.section_id.desc()).all()
    u_books=User_Book.query.filter_by(uid=user_id).all()
    return render_template("userfeed.html",books=books,s_form=s_form,u_books=u_books,user_id=user_id,sections=sections)

def delete_old_received_books():
    seven_days_ago = datetime.now() - timedelta(days=7)
    old_received_books = User_Book.query.filter_by(status='received').filter(User_Book.date_received <= seven_days_ago).all()

    for book in old_received_books:
        db.session.delete(book)

    db.session.commit()

@app.route("/librarianfeed", methods=["GET","POST"])
@login_required
def librarianfeed():
    
    grant_form = GrantForm()
    reject_form = RejectForm()
    revoke_form = RevokeForm()
    books = Book.query.order_by(Book.book_id.desc()).all()
    sections=Section.query.order_by(Section.section_id.desc()).all()

    s_form=SearchForm()
    if s_form.validate_on_submit() and "search_submit" in request.form:
        return redirect(url_for('search_book',q=s_form.search.data))

    if revoke_form.validate_on_submit() and "revoke_submit" in request.form:
        user_book_uid = request.form.get("user_book_uid")
        user_book_bid = request.form.get("user_book_bid")
        user_book = User_Book.query.get((user_book_uid, user_book_bid))
        if user_book:
            db.session.delete(user_book)
            db.session.commit()
            flash("Access revoked successfully!", "success")
        return redirect(url_for("librarianfeed"))

    if grant_form.validate_on_submit() and "grant_submit" in request.form:
        user_book_uid = request.form.get("user_book_uid")
        user_book_bid = request.form.get("user_book_bid")
        user_book = User_Book.query.get((user_book_uid, user_book_bid))
        if user_book:
            user_book.status = "received"
            user_book.date_received = datetime.now()
            db.session.commit()
            flash("Request granted successfully!", "success")
            delete_old_received_books()

    if reject_form.validate_on_submit() and "reject_submit" in request.form:
        user_book_uid = request.form.get("user_book_uid")
        user_book_bid = request.form.get("user_book_bid")
        user_book = User_Book.query.get((user_book_uid, user_book_bid))
        if user_book:
            db.session.delete(user_book)
            db.session.commit()
            flash("Request rejected successfully!", "success")
        return redirect(url_for("librarianfeed"))

    seven_days_ago = datetime.now() - timedelta(days=7)
    old_received_books = User_Book.query.filter_by(status='received').filter(User_Book.date_received <= seven_days_ago).all()
    reminders=[]
    for i in old_received_books:
        reminder_text = f"7 days have passed since {i.u_name} received the book, {i.b_name}"
        reminders.append(reminder_text)
    user_books = User_Book.query.filter_by(status="requested").order_by(User_Book.uid.desc()).all()
    received_books = User_Book.query.filter_by(status="received").order_by(User_Book.uid.desc()).all()
    return render_template("librarianfeed.html", user_books=user_books, grant_form=grant_form, reject_form=reject_form,revoke_form=revoke_form,reminders=reminders,received_books=received_books,books=books,s_form=s_form,sections=sections)

@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route("/addbook",methods=["GET","POST"])
@login_required
@librarian_required
def addbook():
    form=BookForm()
    if form.validate_on_submit():
        try:
            book_file=form.book.data
            filename = secure_filename(book_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            book_file.save(file_path)

            random = secrets.token_hex(8)
            _, exten = os.path.splitext(form.image.data.filename)
            newname = random + exten
            picpath = os.path.join(app.root_path, 'static/bookimages', newname)
            size=(128,128)
            i = Image.open(form.image.data)
            i.thumbnail(size)
            i.save(picpath)

            new_book=Book(bookname=form.bookname.data,author=form.author.data,description=form.description.data,
                          image=newname,file_path=filename,date=datetime.now())
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('librarianfeed'))
        except IntegrityError:
            db.session.rollback()
            return render_template('exists.html')
    if current_user.role=="librarian":
        return render_template('addbook.html', form=form)
    
@app.route("/addsection",methods=["GET","POST"])
@login_required
@librarian_required
def addsection():
    form=SectionForm()
    if form.validate_on_submit():
        try:
            random = secrets.token_hex(8)
            _, exten = os.path.splitext(form.s_image.data.filename)
            newname = random + exten
            picpath = os.path.join(app.root_path, 'static/bookimages', newname)
            size=(128,128)
            i = Image.open(form.s_image.data)
            i.thumbnail(size)
            i.save(picpath)

            new_section=Section(section_name=form.section_name.data,s_description=form.s_description.data,s_image=newname,s_date=datetime.now())
            db.session.add(new_section)
            db.session.commit()
            return redirect(url_for('librarianfeed'))
        except IntegrityError:
            db.session.rollback()
            return render_template('exists.html')
    if current_user.role=="librarian":
        return render_template('addsection.html', form=form)
        

    
@app.route("/editbook/<int:book_id>",methods=["GET","POST"])
@login_required
@librarian_required
def editbook(book_id):
    b=Book.query.filter_by(book_id=book_id).first()
    form=EditBookForm()
    if form.validate_on_submit():
        if form.book.data:
            book_file=form.book.data
            filename = secure_filename(book_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            book_file.save(file_path)
            b.file_path=filename
            db.session.commit()
        if form.author.data:
            b.author=form.author.data
            db.session.commit()
        if form.description.data:
            b.description=form.description.data
            db.session.commit()
        if form.image.data:
            random = secrets.token_hex(8)
            _, exten = os.path.splitext(form.image.data.filename)
            newname = random + exten
            picpath = os.path.join(app.root_path, 'static/bookimages', newname)
            size=(128,128)
            i = Image.open(form.image.data)
            i.thumbnail(size)
            i.save(picpath)
            b.image=newname
            db.session.commit()

        b.date=datetime.now()
        db.session.commit()
        return redirect(url_for('success'))
    if current_user.role=="librarian":
        return render_template('editbook.html', form=form,b=b,book_id=b.book_id)
    
@app.route("/deletebook/<int:book_id>",methods=["GET","POST"])
@login_required
@librarian_required
def deletebook(book_id):
    book=Book.query.filter_by(book_id=book_id).first()
    u_books=User_Book.query.filter_by(bid=book_id).all()
    s_books=Section_Book.query.filter_by(b_id=book_id).all()
    f=Feedback.query.filter_by(b_id=book_id).all()
    if u_books:
        for i in u_books:
            db.session.delete(i)
            db.session.commit()
    if s_books:
        for i in s_books:
            db.session.delete(i)
            db.session.commit()
    if f:
        for i in f:
            db.session.delete(i)
            db.session.commit()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('success'))

@app.route("/lbook/<int:book_id>", methods=["GET", "POST"])
@login_required
@librarian_required
def lbook(book_id):
    b_form=AddbookForm()
    b=Book.query.filter_by(book_id=book_id).first()
    f=Feedback.query.filter_by(b_id=book_id).all()
    sections=Section.query.all()
    section_choices = [(section.section_id, section.section_name) for section in sections]
    b_form.b_section.choices=section_choices
    if b_form.validate_on_submit():
        selected_section_id = b_form.b_section.data
        # Check if the book is already in the section
        existing_entry = Section_Book.query.filter_by(sec_id=selected_section_id, b_id=b.book_id).first()

        if not existing_entry:
            # If not, add the book to the section
            new_section_book = Section_Book(sec_id=selected_section_id, b_id=b.book_id)
            db.session.add(new_section_book)
            db.session.commit()
        return redirect(url_for('success'))
    return render_template('l-book.html',b=b,book_id=book_id,b_form=b_form,f=f)

@app.route('/lsection/<int:section_id>',methods=["GET","POST"])
@login_required
@librarian_required
def lsection(section_id):
    section=Section.query.filter_by(section_id=section_id).first()
    section_books_ids=Section_Book.query.filter_by(sec_id=section_id).all()
    l=[]
    for i in section_books_ids:
        l.append(i.b_id)
    all_books=Book.query.all()
    k=[]
    for i in all_books:
        if i.book_id in l:
            k.append(i)
    return render_template('l-section.html',section=section,k=k)

@app.route('/section/<int:section_id>',methods=["GET","POST"])
@login_required
def section(section_id):
    section=Section.query.filter_by(section_id=section_id).first()
    section_books_ids=Section_Book.query.filter_by(sec_id=section_id).all()
    l=[]
    for i in section_books_ids:
        l.append(i.b_id)
    all_books=Book.query.all()
    k=[]
    for i in all_books:
        if i.book_id in l:
            k.append(i)
    return render_template('section.html',section=section,k=k)

@app.route('/editsection/<int:section_id>',methods=["GET","POST"])
@login_required
@librarian_required
def editsection(section_id):
    section=Section.query.filter_by(section_id=section_id).first()
    form=EditsectionForm()
    if form.validate_on_submit():
        if form.s_description.data:
            section.s_description=form.s_description.data
            db.session.commit()
        if form.s_image.data:
            random = secrets.token_hex(8)
            _, exten = os.path.splitext(form.s_image.data.filename)
            newname = random + exten
            picpath = os.path.join(app.root_path, 'static/bookimages', newname)
            size=(128,128)
            i = Image.open(form.s_image.data)
            i.thumbnail(size)
            i.save(picpath)
            section.s_image=newname
            db.session.commit()
        section.s_date=datetime.now()
        db.session.commit()
        return redirect(url_for('success'))
    if current_user.role=="librarian":
        return render_template('editsection.html', form=form,section=section)
    
@app.route('/deletesection/<int:section_id>',methods=["GET","POST"])
@login_required
@librarian_required
def deletesection(section_id):
    section=Section.query.filter_by(section_id=section_id).first()
    s_books=Section_Book.query.filter_by(sec_id=section_id).all()
    if s_books:
        for i in s_books:
            db.session.delete(i)
            db.session.commit()
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for('success'))

@app.route("/search/<q>",methods=["GET","POST"])
@login_required
def search_book(q):
    l=Book.query.filter(Book.bookname.ilike(f"%{q}%")).all()
    k=Section.query.filter(Section.section_name.ilike(f"%{q}%")).all()
    return render_template("search.html",l=l,k=k)

@app.route("/book/<int:book_id>", methods=["GET", "POST"])
@login_required
def book(book_id):
    b=Book.query.filter_by(book_id=book_id).first()
    ub=User_Book.query.filter_by(bid=book_id).all()
    ub1=User_Book.query.filter_by(bid=book_id,uid=current_user.user_id).first()
    u=User_Book.query.all()
    fed = FeedbackForm()
    if ub1:
        if ub1.status=='requested':
            req=CancelreqForm()
            if req.validate_on_submit():
                userbook=User_Book.query.filter_by(uid=current_user.user_id,bid=book_id).first()
                db.session.delete(userbook)
                db.session.commit()
                return redirect(url_for('book',book_id=book_id))
        elif ub1.status=='received':
            req=ReturnForm()
            if req.validate_on_submit() and "return" in request.form:
                userbook=User_Book.query.filter_by(uid=current_user.user_id,bid=book_id,status='received').first()
                db.session.delete(userbook)
                db.session.commit()
                return redirect(url_for('book',book_id=book_id))
            if fed.validate_on_submit() and "fed_submit" in request.form:
                existing_feedback = Feedback.query.filter_by(u_id=current_user.user_id,b_id=b.book_id).first()
                if existing_feedback:
                    existing_feedback.feedback=fed.feedback.data
                    db.session.commit()
                    return redirect(url_for('book',book_id=book_id))
                else:
                    f=Feedback(u_id=current_user.user_id,b_id=b.book_id,uname=current_user.username,bname=b.bookname,feedback=fed.feedback.data)
                    db.session.add(f)
                    db.session.commit()
                    return redirect(url_for('book',book_id=book_id))
    else:
        req=RequestForm()
        if req.validate_on_submit():
            if len(User_Book.query.filter_by(uid=current_user.user_id).all()) >= 5:
                return redirect(url_for('limit'))
            new_userbook=User_Book(uid=current_user.user_id,bid=book_id,u_name=current_user.username,b_name=b.bookname,status='requested')
            db.session.add(new_userbook)
            db.session.commit()
            return redirect(url_for('book',book_id=book_id))
    k=Feedback.query.filter_by(b_id=b.book_id).all()
    return render_template('book.html',b=b,ub=ub,req=req,fed=fed,k=k,ub1=ub1)

def get_section_counts():
    # Join Section and Section_Book models on sec_id
    section_counts = db.session.query(Section.section_name, db.func.count(Section_Book.sec_id)). \
        join(Section_Book, Section.section_id == Section_Book.sec_id). \
        group_by(Section.section_name).all()

    # section_counts will be a list of tuples (section_name, count)
    return section_counts


@app.route('/profile/<int:user_id>', methods=["GET","POST"])
@login_required
def profile(user_id):
    user=User.query.filter_by(user_id=user_id).first()
    total_books=len(Book.query.all())
    my_books=len(User_Book.query.filter_by(uid=user.user_id,status='received').all())
    books_requested=len(User_Book.query.filter_by(uid=user.user_id,status='requested').all())
    section_spread=get_section_counts()
    categories = ['Total Books', 'My Books', 'Books Requested']
    counts = [total_books, my_books, books_requested]
    form=NotesForm()
    if any(counts):
        # Plotting the bar chart
        plt.bar(categories, counts, color=['blue', 'green', 'orange'])
        plt.xlabel('Categories', fontweight='bold')
        plt.ylabel('Counts', fontweight='bold')
        plt.title('Counts of Total Books, My Books, and Requested Books')
        plt.grid(axis='y')
        plt.yticks(range(0, max(counts) + 4))
        save_dir = 'static/bookimages'
        image_path1 = os.path.join(save_dir, 'bar_chart.png')
        plt.savefig(image_path1)
        plt.close()

    sections = [section[0] for section in section_spread]
    if sections:
        cts = [section[1] for section in section_spread]
        # Plotting the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(cts, labels=sections, autopct='%1.1f%%', startangle=140)
        plt.title('Section Spread')
        image_path2 = os.path.join(save_dir, 'pie_chart.png')
        plt.savefig(image_path2)
        plt.close()
    
    notes=User_Notes.query.filter_by(id_u=current_user.user_id).all()
    max_n_id = db.session.query(func.max(User_Notes.n_id)).filter_by(id_u=current_user.user_id).scalar()
    next_n_id = (max_n_id or 0) + 1
    if form.validate_on_submit():
        user_notes=User_Notes(n_id=next_n_id,id_u=current_user.user_id,notes=form.notes.data)
        db.session.add(user_notes)
        db.session.commit()
        return redirect(url_for('profile',user_id=current_user.user_id))
    return render_template('profile.html',user=user,bar_chart='bar_chart.png', pie_chart='pie_chart.png',counts=counts,sections=sections,form=form,notes=notes)

@app.route('/statspage/<int:user_id>', methods=["GET","POST"])
@login_required
@librarian_required
def statspage(user_id):
    user=User.query.filter_by(user_id=user_id).first()
    total_books=len(Book.query.all())
    books_issued=len(User_Book.query.filter_by(status='received').all())
    book_requests=len(User_Book.query.filter_by(status='requested').all())
    section_spread=get_section_counts()
    book_counts = db.session.query(User_Book.b_name, func.count(User_Book.b_name)).group_by(User_Book.b_name).all()
    book_counts_list = [(b_name, count) for b_name, count in book_counts]
    categories = ['Total Books', 'Book Requests', 'Books Issued']
    counts = [total_books, book_requests, books_issued]
    form=NotesForm()
    if any(counts):
        # Plotting the bar chart
        plt.bar(categories, counts, color=['blue', 'green', 'orange'])
        plt.xlabel('Categories', fontweight='bold')
        plt.ylabel('Counts', fontweight='bold')
        plt.title('Counts of Total Books, Book Requests and Books Issued')
        plt.grid(axis='y')
        plt.yticks(range(0, max(counts) + 4))
        save_dir = 'static/bookimages'
        image_path1 = os.path.join(save_dir, 'bar_chart1.png')
        plt.savefig(image_path1)
        plt.close()
    b_names = [item[0] for item in book_counts_list]
    counts = [item[1] for item in book_counts_list]
    if b_names:
        # Create bar graph
        plt.figure(figsize=(10, 6))
        plt.bar(b_names, counts)
        plt.xlabel('Book Names', fontweight='bold')
        plt.ylabel('Number of books requested/received by users', fontweight='bold')
        plt.title('Book Management')
        plt.yticks(range(0, max(counts) + 4))

        # Save the plot to a file
        plot_file = os.path.join('static', 'bookimages', 'book_counts_bar.png')
        plt.savefig(plot_file)
        plt.close()
    sections = [section[0] for section in section_spread]
    if sections:
        cts = [section[1] for section in section_spread]
        # Plotting the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(cts, labels=sections, autopct='%1.1f%%', startangle=140)
        plt.title('Section Spread')
        image_path2 = os.path.join(save_dir, 'pie_chart1.png')
        plt.savefig(image_path2)
        plt.close()
    notes=User_Notes.query.filter_by(id_u=current_user.user_id).all()
    max_n_id = db.session.query(func.max(User_Notes.n_id)).filter_by(id_u=current_user.user_id).scalar()
    next_n_id = (max_n_id or 0) + 1
    if form.validate_on_submit():
        user_notes=User_Notes(n_id=next_n_id,id_u=current_user.user_id,notes=form.notes.data)
        db.session.add(user_notes)
        db.session.commit()
        return redirect(url_for('statspage',user_id=current_user.user_id))
    return render_template('statspage.html',user=user,bar_chart1='bar_chart1.png', pie_chart1='pie_chart1.png',counts=counts,sections=sections,b_names=b_names,book_counts_bar='book_counts_bar.png',form=form,notes=notes)


@app.route('/booklimit')
@login_required
def limit():
    return render_template('limit.html')

@app.route('/success')
@login_required
@librarian_required
def success():
    return render_template('success.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



#------RUN------
if __name__=='__main__':
    app.run(debug=True)