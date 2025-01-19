from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import desc
from slugify import slugify
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)  # Made optional
    author = db.Column(db.String(100), nullable=True, default='Admin')  # Made optional with default
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref='posts')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary='post_tags', backref='posts')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

# Association table
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Context processors
@app.context_processor
def utility_processor():
    def get_categories():
        return Category.query.all()
    
    def get_tags():
        return Tag.query.all()
    
    return dict(get_categories=get_categories, get_tags=get_tags)

# Template filters
@app.template_filter('format_date')
def format_date_filter(date):
    if isinstance(date, datetime):
        return date.strftime('%B %d, %Y')
    return date

@app.template_filter('slugify')
def slugify_filter(s):
    return slugify(s)

# Routes
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', 
                         posts=pagination.items,
                         current_page=page,
                         total_pages=pagination.pages)

@app.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    related_posts = Post.query.filter_by(category_id=post.category_id).filter(Post.id != post.id).limit(3).all()
    return render_template('post.html', post=post, related_posts=related_posts)

@app.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category_id=category.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('category.html', 
                         category=category,
                         posts=pagination.items,
                         current_page=page,
                         total_pages=pagination.pages)

@app.route('/tag/<slug>')
def tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('tag.html', 
                         tag=tag,
                         posts=pagination.items,
                         current_page=page,
                         total_pages=pagination.pages)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        search_term = f"%{query}%"
        posts = Post.query.filter(Post.title.ilike(search_term) | 
                                Post.content.ilike(search_term)).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)

if __name__ == '__main__':
    with app.app_context():
        # Delete the existing database
        import os
        if os.path.exists('instance/blog.db'):
            os.remove('instance/blog.db')
        
        # Create all tables
        db.create_all()
        
        # Add initial data
        tech_category = Category(name='Technology', slug='technology')
        db.session.add(tech_category)
        db.session.commit()

        # Add sample post
        sample_post = Post(
            title='Welcome to Tech Insights',
            slug='welcome-to-tech-insights',
            content='This is our first blog post about technology...',
            category_id=tech_category.id,
            author='Admin'
        )
        db.session.add(sample_post)
        db.session.commit()

    app.run(debug=True)
