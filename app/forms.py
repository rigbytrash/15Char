from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError


class PostForm(FlaskForm):
    post = TextAreaField('post', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class ReplyForm(FlaskForm):
    post = TextAreaField('post', validators=[DataRequired()])

class EmojiForm(FlaskForm):
    EMOJI_CHOICES = [
    ('❤️', '❤️ Heart'),
    ('😊', '😊 Smiling Face'),
    ('😃', '😃 Grinning Face with Big Eyes'),
    ('😍', '😍 Heart Eyes'),
    ('😎', '😎 Smiling Face with Sunglasses'),
    ('😇', '😇 Smiling Face with Halo'),
    ('🥰', '🥰 Smiling Face with Hearts'),
    ('😋', '😋 Face Savoring Food'),
    ('😜', '😜 Winking Face with Tongue'),
    ('😐', '😐 Neutral Face'),
    ('😢', '😢 Crying Face'),
    ('😡', '😡 Angry Face'),
    ('😳', '😳 Flushed Face'),
    ('😷', '😷 Face with Medical Mask'),
    ('🤔', '🤔 Thinking Face'),
    ('😭', '😭 Loudly Crying Face'),
    ('🤗', '🤗 Hugging Face'),
    ('🤣', '🤣 Rolling on the Floor Laughing'),
    ('😴', '😴 Sleeping Face'),
    ('😮', '😮 Surprised Face'),
]

    emoji = SelectField('Select Emoji', choices=EMOJI_CHOICES, validators=[DataRequired()])
    submit = SubmitField('Change')