from flask import *
from app import app, models, db
from flask import render_template, flash, request
from .forms import PostForm, LoginForm, RegisterForm, ReplyForm, EmojiForm
import datetime
import json
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from faker import Faker
import random
from sqlalchemy import or_
import logging


bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
logging.basicConfig(filename='app.log', level=logging.DEBUG)
faker_logger = logging.getLogger('faker')
faker_logger.setLevel(logging.CRITICAL)


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


def save_post(form):
    new_post = models.Post(
        text=form.post.data, owner_id=current_user.id, 
        timestamp=datetime.datetime.utcnow())
    db.session.add(new_post)
    db.session.commit()
    flash("You Posted: " + str(form.post.data))


def process_posts(posts):
    for post in posts:
        post.user_has_liked = models.Like.query.filter_by(
            user_id=current_user.id, post_id=post.id).first() is not None
        post.owner_username = models.User.query.filter_by(
            id=post.owner_id).first().emoji
        post.owner_username += " " + models.User.query.filter_by(
            id=post.owner_id).first().username
        post.reply_count = models.Reply.query.filter_by(
            parent_id=post.id).count()
        post.user_has_followed = models.Follow.query.filter_by(
            follower_id=current_user.id, followed_id=post.owner_id).first() is not None


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            logging.info('User %s logged in', user.username)
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password. Please try again.', 'danger')

    return render_template('login.html', title="Login", form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logging.info('User %s logged out', current_user.username)
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    posts = models.Post.query.all()
    if form.validate_on_submit():
        if len(form.post.data) > 15:
            flash("Error: Post should be 15 characters or less.", 'danger')
        else:
            save_post(form)
    posts = models.Post.query.all()
    process_posts(posts)
    return render_template('index.html', title="Home", form=form, 
                           posts=posts)


@app.route('/user_posts/<int:user_id>', methods=['GET'])
@login_required
def user_posts(user_id):
    user = models.User.query.get(user_id)
    if user:
        user_posts = models.Post.query.filter_by(owner_id=user.id).all()
        process_posts(user_posts)
        return render_template(
            'user_posts.html', title="User Posts", user=user, 
            user_posts=user_posts)
    else:
        flash('User not found', 'danger')
        return redirect(url_for('index'))


@app.route('/view_post/<int:post_id>', methods=['GET'])
@login_required
def view_post(post_id):
    post = models.Post.query.get(post_id)
    if not post:
        return redirect(url_for('index'))

    post.owner_username = models.User.query.filter_by(
        id=post.owner_id).first().username
    post.owner_emoji = models.User.query.filter_by(
        id=post.owner_id).first().emoji
    post.user_has_liked = models.Like.query.filter_by(
        user_id=current_user.id, post_id=post.id).first() is not None
    post.reply_count = models.Reply.query.filter_by(parent_id=post.id).count()

    if post:
        replies = models.Reply.query.filter_by(parent_id=post.id).all()
        for reply in replies:
            reply.owner_username = models.User.query.filter_by(
                id=reply.owner_id).first().username
            reply.owner_emoji = models.User.query.filter_by(
                id=reply.owner_id).first().emoji
        return render_template(
            'view_post.html', title="View Post", replies=replies, post=post)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))


@app.route('/reply_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def reply_post(post_id):
    post = models.Post.query.get(post_id)
    post.user_has_liked = models.Like.query.filter_by(
        user_id=current_user.id, post_id=post.id).first() is not None
    post.owner_username = models.User.query.filter_by(
        id=post.owner_id).first().username
    post.reply_count = models.Reply.query.filter_by(
        parent_id=post.id).count()

    if post:
        form = ReplyForm()

        if form.validate_on_submit():
            if len(form.post.data) > 15:
                flash("Error: Reply should be 15 characters or less.", 
                      'danger')
            else:
                new_reply = models.Reply(
                    text=form.post.data,
                    owner_id=current_user.id,
                    timestamp=datetime.datetime.utcnow(),
                    parent_id=post.id
                )
                db.session.add(new_reply)
                db.session.commit()
                flash("You replied: \"" + str(form.post.data) + "\" to " + 
                      models.User.query.filter_by(
                    id=post.owner_id).first().username + "'s post")
                next_url = request.args.get('next') or url_for('index')
                return redirect(next_url)

        return render_template(
            'reply_post.html', title="Reply To Post", post=post, form=form)
    else:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = models.User.query.filter_by(
            username=form.username.data).first()
        if existing_user:
            flash(
                'Username already exists. Please choose a different username.', 
                'danger')
            return render_template(
                'register.html', title="Register", form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = models.User(
            username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 
              'success')
        return redirect(url_for('login'))

    return render_template('register.html', title="Register", form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return redirect(url_for('user_posts', user_id=current_user.id))


@app.route('/like', methods=['POST'])
def like():
    data = json.loads(request.data)
    post_id = int(data.get('post_id'))
    post = models.Post.query.get(post_id)
    liked = True
    existing_like = models.Like.query.filter_by(
        user_id=current_user.id, post_id=post.id).first()

    if existing_like:
        liked = False
        db.session.delete(existing_like)
        post.likes -= 1
    else:
        new_like = models.Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        post.likes += 1

    db.session.commit()
    return json.dumps(
        {'status': 'OK', 'likes': post.likes, 'user_has_liked': liked})


@app.route('/wipe', methods=['GET', 'POST'])
def wipe():
    posts = models.Post.query.all()
    for post in posts:
        db.session.delete(post)

    replies = models.Reply.query.all()
    for reply in replies:
        db.session.delete(reply)

    users = models.User.query.all()
    for user in users:
        db.session.delete(user)

    follows = models.Follow.query.all()
    for follow in follows:
        db.session.delete(follow)

    likes = models.Like.query.all()
    for like in likes:
        db.session.delete(like)

    # Commit the changes to the database
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = models.Post.query.get(post_id)
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

    if current_user.id != post.owner_id:
        abort(403)  # Forbidden

    # Delete the post and its replies
    replies = models.Reply.query.filter_by(parent_id=post.id).all()
    for reply in replies:
        db.session.delete(reply)
    db.session.delete(post)
    db.session.commit()
    flash('Post and its replies have been deleted', 'success')

    # Get the 'next' parameter from the request or default to the index page
    next_url = request.args.get('next') or url_for('index')
    return redirect(next_url)


@app.route('/delete_reply/<int:reply_id>', methods=['GET', 'POST'])
@login_required
def delete_reply(reply_id):
    reply = models.Reply.query.get(reply_id)
    if not reply:
        flash('Reply not found', 'danger')
        return redirect(url_for('index'))

    if current_user.id != reply.owner_id:
        abort(403)  # Forbidden

    db.session.delete(reply)
    db.session.commit()
    flash('Reply has been deleted', 'success')

    # Get the 'next' parameter from the request or default to the index page
    next_url = request.args.get('next') or url_for('index')
    return redirect(next_url)


fake = Faker()


@app.route('/generate_test_data', methods=['GET'])
def generate_test_data():
    auth = request.authorization
    if not auth or not (auth.username == 'admin' and auth.password == 'hamzasiddique'):
        return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    
    # Create test users
    for _ in range(5):
        username = fake.user_name()
        password = fake.password()
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = models.User(username=username, password=hashed_password)
        db.session.add(new_user)

    db.session.commit()

    # Create test posts
    users = models.User.query.all()
    for _ in range(10):
        random_user = fake.random_element(elements=users)
        post_text = fake.text(max_nb_chars=15)
        new_post = models.Post(
            text=post_text, owner_id=random_user.id, 
            timestamp=fake.date_time_this_year())
        db.session.add(new_post)

    db.session.commit()

    # Create test replies
    posts = models.Post.query.all()
    for _ in range(15):
        random_post = fake.random_element(elements=posts)
        random_user = fake.random_element(elements=users)
        reply_text = fake.text(max_nb_chars=30)
        new_reply = models.Reply(
            text=reply_text,
            owner_id=random_user.id,
            timestamp=fake.date_time_this_year(),
            parent_id=random_post.id
        )
        db.session.add(new_reply)

        db.session.commit()

    flash('Test data generated successfully', 'success')
    return redirect(url_for('index'))


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    posts = models.Post.query.filter(
        or_(models.Post.text.like(f'%{query}%'))).all()
    process_posts(posts)
    return render_template('search_results.html',
                           title="Search Results", query=query, posts=posts)


@app.route('/change_emoji', methods=['GET', 'POST'])
@login_required
def change_emoji():
    form = EmojiForm()
    user = models.User.query.get(current_user.id)
    if form.validate_on_submit():
        current_user.emoji = form.emoji.data
        db.session.commit()
        next_url = request.args.get('next') or url_for('index')
        return redirect(next_url)

    return render_template('change_emoji.html',
                           title="Change Emoji", user=user, form=form)

@app.route('/view_likes/<int:post_id>', methods=['GET'])
@login_required
def view_likes(post_id):
    post = models.Post.query.get(post_id)
    post.user_has_liked = models.Like.query.filter_by(
            user_id=current_user.id, post_id=post.id).first() is not None
    post.owner_username = models.User.query.filter_by(
        id=post.owner_id).first().emoji
    post.owner_username += " " + models.User.query.filter_by(
        id=post.owner_id).first().username
    post.reply_count = models.Reply.query.filter_by(
        parent_id=post.id).count()

    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('index'))

    # Retrieve likes for the post
    likes = models.Like.query.filter_by(post_id=post.id).all()
    for like in likes:
        like.owner_emoji = models.User.query.filter_by(
                            id=like.user_id).first().emoji
        like.owner_username = models.User.query.filter_by(
                                id=like.user_id).first().username


    return render_template('view_likes.html', 
                            title='View Likes', post=post, likes=likes)

#follow route that uses ajax to follow a user
@app.route('/follow', methods=['POST'])
def follow():
    data = json.loads(request.data)
    post = models.Post.query.get(data.get('post_id'))
    user_id = post.owner_id
    user = models.User.query.get(user_id)
    followed = True
    txt = "Follow"
    existing_follow = models.Follow.query.filter_by(
        follower_id=current_user.id, followed_id=user.id).first()

    if existing_follow:
        followed = False
        db.session.delete(existing_follow)
    else:
        new_follow = models.Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(new_follow)
        txt = "Unfollow"

    db.session.commit()
    return json.dumps(
        {'status': 'OK', 'btntxt': txt, 'user_has_followed': followed})


@app.route('/following', methods=['GET'])
@login_required
def following():
    # Retrieve the users the current user is following
    following_users = [follow.followed_id for follow in models.Follow.query.filter_by(follower_id=current_user.id).all()]

    # Retrieve posts from the users the current user is following
    following_posts = models.Post.query.filter(models.Post.owner_id.in_(following_users)).all()

    # Process posts as needed
    process_posts(following_posts)

    return render_template('following.html', title='Following', posts=following_posts)

