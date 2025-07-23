from database.models import *
from sqlalchemy.orm import Session

def add_user(user_id: str, complites: str, admin: bool = False):
    with Session(autoflush=False, bind=engine) as db:
        new_user = User(user_id = user_id, admin = admin, complite_tasks = complites)
        db.add(new_user)
        db.commit()
        return f"Чел {new_user.user_id} супер успешно добавлен"

def select_all_users():
    with Session(autoflush=False, bind=engine) as db:
        all_users = db.query(User).all()
        count = ""
        for user in all_users:
            count += f"\n{user.id}; {user.user_id}; {user.complite_tasks}" if user.admin == False else f"\n{user.id}; {user.user_id}; {user.complite_tasks} - АДМИН"
        return count
    
def select_one_user_from_id(id: int):
    with Session(autoflush=False, bind=engine) as db:
        user_count = db.get(User, id)
        return f"{user_count.user_id}; {user_count.complite_tasks}"
    
def select_one_user_from_use(user_id: str):
    with Session(autoflush=False, bind=engine) as db:
        this_user = db.query(User).filter(User.user_id == user_id).first()
        return this_user.id

def update_user_complites(id_us: int, complites: str):
    with Session(autoflush=False, bind=engine) as db:
        data_user = db.query(User).filter(User.id==id_us).first()
        if data_user != None:
            data_user.complite_tasks += complites
            db.commit()
            return f"{data_user.user_id}; {data_user.complite_tasks}"
        
def delete_user(id):
    with Session(autoflush=False, bind=engine) as db:
        user_for_delete = db.query(User).filter(User.id==id).first()
        db.delete(user_for_delete)
        db.commit()
        return "Чел успешно удалён"

def complites_use(user_id):
    return select_one_user_from_id(select_one_user_from_use(user_id)).split(";")[1][:-2].replace(" ", "").split(",")

def complites_id(id):
    return select_one_user_from_id(id).split(";")[1][:-2].replace(" ", "").split(",")

def is_admin(user_id):
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.user_id==user_id).first()
        return True if user.admin == True else False
    
