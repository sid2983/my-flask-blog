

import email
import secrets,os
from turtle import pos, title
from PIL import Image
from flask import render_template,redirect,url_for,flash,request,abort,session
from flaskblog import app,db,bcrypt,blueprint,mail
from flaskblog.forms import Registration_form,Login_form,UpdateAccountForm,PostForm,RequestResetForm,Reset_Password_Form
from flaskblog.models import User, Post, OAuth,Oauthuser
from flask_login import login_user, current_user,logout_user,login_required
from flask_dance.contrib.google import google
from flask_dance.consumer import oauth_authorized, oauth_error
from sqlalchemy.orm.exc import NoResultFound
from flask_mail import Message

from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
# from flask_dance.contrib.google import make_google_blueprint,google


# blueprint = make_google_blueprint(client_id='885804391863-epgi238upfo9unp0626o7460i661t2j4.apps.googleusercontent.com',client_secret='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',offline=True,scope=['profile','email','openid'])
# app.register_blueprint(blueprint,url_prefix='/login/google')



blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@app.route("/")
def home():
    page=request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template("home.html",posts=posts)

@app.route("/about")
def about():
    return render_template("about.html",title='About')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Registration_form()
    if form.validate_on_submit():
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.uname.data, email=form.email.data, password = hashed_passwd)
        db.session.add(user)
        db.session.commit()
        flash(f' Your account has been created! You are now able to log in ','success')
        return redirect(url_for('login'))
        
    return render_template('register.html',title='Register',form = form)


@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login_form()
    if form.validate_on_submit():
        # if form.password.data == 'sid2983$&':
        #     flash('You have been logged in!','success')
        #     return redirect(url_for('home'))
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Success!','success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccesfull. Please check your Email Id and password','danger')

    return render_template('auth.html',title='Login',form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='sid24000576@gmail.com',recipients=[user.email])

    msg.body = f""" To reset your password, visit the following link:
    {url_for('reset_token',token=token,_external=True)}

    If you didn't make this request, then simply ignore this email and no changes will be made. 
    """
    mail.send(msg)




@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password. ','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))

    form = Reset_Password_Form()
    if form.validate_on_submit():
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_passwd
        db.session.commit()
        flash(f' Your password has been updated! You are now able to log in ','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route('/account',methods=['POST','GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.img_file = picture_file
        current_user.username = form.uname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated','success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.uname.data = current_user.username
        form.email.data = current_user.email
        image_file = url_for('static',filename='profile_pics/' + current_user.img_file)
        return render_template('account.html',title='Account',image_file=image_file,form=form)





@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form = form,legend='New Post')


@app.route("/post/<int:post_id>",methods=['GET','POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)


@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content= form.content.data
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')


@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('home'))




@app.route("/user/<string:username>")
def user_posts(username):
    page=request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template("user_posts.html",posts=posts,user=user)


@app.route('/login/google')
def google_login():
    if not google.authorized:
        return render_template("google.login")
    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text
    # email = resp.json()['email']
    



# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="error")
        return False

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            token=token,
        )

    if oauth.user:
        # If this OAuth token already has an associated local account,
        # log in that local user account.
        # Note that if we just created this OAuth token, then it can't
        # have an associated local account yet.
        login_user(oauth.user)
        flash("Successfully signed in with GitHub.")

    else:
        # If this OAuth token doesn't have an associated local account,
        # create a new local user account for this user. We can log
        # in that account as well, while we're at it.
        user = Oauthuser(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on GitHub!
            email=google_info["email"],
            username=google_info["email"],
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with Google.")

    # Since we're manually creating the OAuth model in the database,
    # we should return False so that Flask-Dance knows that
    # it doesn't have to do it. If we don't return False, the OAuth token
    # could be saved twice, or Flask-Dance could throw an error when
    # trying to incorrectly save it for us.
    return False

    
# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")



