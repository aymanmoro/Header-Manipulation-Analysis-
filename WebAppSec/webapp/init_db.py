from app import app, db, Category, Tag, Post
from slugify import slugify
from datetime import datetime

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Add categories if they don't exist
        categories = ['Technology', 'Programming', 'Design', 'Data Science']
        for name in categories:
            if not Category.query.filter_by(name=name).first():
                category = Category(name=name, slug=slugify(name))
                db.session.add(category)

        # Add some tags
        tags = ['Python', 'JavaScript', 'Web Development', 'AI', 'Machine Learning']
        for name in tags:
            if not Tag.query.filter_by(name=name).first():
                tag = Tag(name=name, slug=slugify(name))
                db.session.add(tag)

        # Commit the changes
        db.session.commit()

        # Add a sample post if no posts exist
        if not Post.query.first():
            tech_category = Category.query.filter_by(name='Technology').first()
            python_tag = Tag.query.filter_by(name='Python').first()
            
            sample_post = Post(
                title='Getting Started with Flask',
                slug='getting-started-with-flask',
                content='This is a sample post about Flask web development...',
                excerpt='Learn how to build web applications with Flask',
                author='Admin',
                category_id=tech_category.id,
                date_posted=datetime.utcnow()
            )
            
            if python_tag:
                sample_post.tags.append(python_tag)
            
            db.session.add(sample_post)
            db.session.commit()

if __name__ == '__main__':
    init_database()
