import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User, Todo, Category
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db:
        drop_all()
        create_db_and_tables()
        
        bob = User(username='bob', email='bob@mail.com')
        bob.set_password("bobpass")

        db.add(bob)
        db.commit()
        db.refresh(bob)

        new_todo = Todo(text='Wash dishes', user_id=bob.id)

        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)

        print("Database Initialized")

@cli.command()
def add_task(username:str, task:str):
    # Task 4.1 code here. Remove the line with "pass" below once completed
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        user.todos.append(Todo(text=task))
        db.add(user)
        db.commit()
        print("Task added for user")
    pass

@cli.command()
def toggle_todo(todo_id:int, username:str):
    # Task 4.2 code here. Remove the line with "pass" below once completed
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("This todo doesn't exist")
            return
        if todo.user.username != username:
            print(f"This todo doesn't belong to {username}")
            return

        todo.toggle()
        db.add(todo)
        db.commit()

        print(f"Todo item's done state set to {todo.done}")
    pass

@cli.command()
def list_todo_categories(todo_id:int, username:str):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
        elif not todo.user.username == username:
            print("Todo doesn't belong to that user")
        else:
            print(f"Categories: {todo.categories}")

@cli.command()
def create_category(username:str, cat_text:str):        
    # Task 5.4 code here. Remove the line with "pass" below once completed
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return

        category = db.exec(select(Category).where(Category.text== cat_text, Category.user_id == user.id)).one_or_none()
        if category:
            print("Category exists! Skipping creation")
            return
        
        category = Category(text=cat_text, user_id=user.id)
        db.add(category)
        db.commit()

        print("Category added for user")

@cli.command()
def list_user_categories(username:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        categories = db.exec(select(Category).where(Category.user_id == user.id)).all()
        print([category.text for category in categories])

@cli.command()
def assign_category_to_todo(username:str, todo_id:int, category_text:str):
    # Task 5.6 code here. Remove the line with "pass" below once completed
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        
        category = db.exec(select(Category).where(Category.text == category_text, Category.user_id==user.id)).one_or_none()
        if not category:
            category = Category(text=category_text, user_id=user.id)
            db.add(category)
            db.commit()
            print("Category didn't exist for user, creating it")
        
        todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id==user.id)).one_or_none()
        if not todo:
            print("Todo doesn't exist for user")
            return
        
        todo.categories.append(category)
        db.add(todo)
        db.commit()
        print("Added category to todo")

# Task 1 - Output each todo's ID, text, username and done status
@cli.command()
def list_todos():
    with get_session() as db:
        todos = db.exec(select(Todo)).all()
        for todo in todos:
            print(f"ID: {todo.id} | Text: {todo.text} | User: {todo.user.username} | Done: {todo.done}")

# Task 2 - Delete a todo by ID
@cli.command()
def delete_todo(todo_id: int):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
            return
        db.delete(todo)
        db.commit()
        print(f"Todo {todo_id} deleted")

# Task 3 - Mark all of a user's todos as complete
@cli.command()
def complete_all(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        todos = db.exec(select(Todo).where(Todo.user_id == user.id)).all()
        for todo in todos:
            todo.done = True
        db.commit()
        print(f"All todos for {username} marked as complete")

if __name__ == "__main__":
    cli()