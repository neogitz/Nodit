from ext import app, db
from models import User, Thread, Post, Comment, Nod
from werkzeug.security import generate_password_hash

users = [
    {"username": "JohnDoe", "gender": "Male", "country": "United States", "age": 24, "img": "mesa.png",
     "role": "user"},
    {"username": "JaneDoe", "gender": "Female", "country": "United States", "age": 32, "img": "family.jpg",
     "role": "user"},
    {"username": "admin", "country": "Georgia", "gender": "Male", "birthday": "2025-06-26", "age": 200,
     "img": "emptypfp.png", "role": "Admin"}
]

with app.app_context():
    try:
        db.drop_all()
        print("Dropping all tables")
        db.create_all()
        print("Creating all tables")

        for user in users:
            try:
                print(f"Inserting {user['username']}")
                new_user = User(
                    username=user["username"],
                    password=generate_password_hash("adminuser"),
                    gender=user["gender"],
                    country=user["country"],
                    pfp=user["img"],
                    role=user["role"]
                )
                db.session.add(new_user)
            except Exception as e:
                print(f"Error inserting {user['username']}: {e}")

        db.session.commit()
        print("Saved all users")

        user1 = User.query.filter_by(username="JohnDoe").first()
        user2 = User.query.filter_by(username="JaneDoe").first()

        thread = Thread(title="Welcome Thread", creator=user1, description="Welcoming description6")
        db.session.add(thread)
        db.session.commit()

        post = Post(title="Welcome title", text="Hello everyone!", threadID=thread.threadID, creator=user2)
        db.session.add(post)
        db.session.commit()

        comment = Comment(text="Thanks!", threadID=thread.threadID, postID=post.postID, userID=user1.id)
        db.session.add(comment)
        db.session.commit()

        new_nod = Nod(
            user_id=1,
            post_id=1,
        )

        db.session.add(new_nod)
        db.session.commit()
        print("New Nod added")

    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")
