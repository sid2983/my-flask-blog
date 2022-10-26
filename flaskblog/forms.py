
from turtle import title
from flask import Flask, render_template,redirect,request,url_for,flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,SubmitField,PasswordField,RadioField,TextAreaField,DateField,EmailField,BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user
from flask_ckeditor import CKEditorField




class Registration_form(FlaskForm):
    fname = StringField('First Name ')
    lname = StringField('Last Name ')
    uname = StringField('Username ',validators=[DataRequired(),Length(min=2,max=20)])
    email = EmailField('Email ',validators=[DataRequired(),Email()])
    password = PasswordField('Password ',validators=[DataRequired()])
    c_password = PasswordField(' Confirm Password ',validators=[DataRequired(),EqualTo('password')])
    check_agree = BooleanField('I Agree.',validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please try a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please try a different username.')


class Login_form(FlaskForm):
    
    email = EmailField('Email ',validators=[DataRequired(),Email()],render_kw={"placeholder":"Email Address"})
    password = PasswordField('Password ',validators=[DataRequired()],render_kw={"placeholder":"Password"})
    remember = BooleanField('Remember me')
    sumbit = SubmitField('Login')




class UpdateAccountForm(FlaskForm):
    fname = StringField('First Name ')
    lname = StringField('Last Name ')
    uname = StringField('Username ',validators=[DataRequired(),Length(min=2,max=20)])
    email = EmailField('Email ',validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please try a different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please try a different username.')


class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = CKEditorField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = EmailField('Email ',validators=[DataRequired(),Email()],render_kw={"placeholder":"Email Address"})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register first.')

class Reset_Password_Form(FlaskForm):
    password = PasswordField('Password ',validators=[DataRequired()],render_kw={"placeholder":" New Password"})
    c_password = PasswordField(' Confirm Password ',validators=[DataRequired(),EqualTo('password')],render_kw={"placeholder":"Confirm Password"})
    submit = SubmitField('Reset Password')