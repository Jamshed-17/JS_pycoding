import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database.models import *
# from models import *
from sqlalchemy.orm import Session

def add_user(user_id: str, complites: str = "", admin: bool = False, page_number: int = 1):
    """Добавляет пользователя
    Поля:
    user_id - telegram username
    complites - выполненые таски (дефолт - отстствие)
    admin - является ли пользователь администратором"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        if db.query(User).filter(User.user_id==user_id).first(): return "Пользователь уже существует"
        else:
            new_user = User(user_id = user_id, admin = admin, complite_tasks = complites, page_number = page_number)
            db.add(new_user)
            db.commit()
            return f"Чел {new_user.user_id} супер успешно добавлен"

def select_all_users():
    """Возвращает всех пользователей"""
    with Session(autoflush=False, bind=engine) as db:
        all_users = db.query(User).all()
        count = ""
        for user in all_users:
            count += f"\n{user.id}; {user.user_id}; {user.complite_tasks}" if user.admin == False else f"\n{user.id}; {user.user_id}; {user.complite_tasks} - АДМИН"
        return count
    
def select_one_user_from_id(id: int):
    """Возвращает пользователя по id"""
    with Session(autoflush=False, bind=engine) as db:
        user_count = db.get(User, id)
        return f"{user_count.user_id}; {user_count.complite_tasks}"
    
def select_one_user_from_use(user_id: str):
    """Возвращает пользователя по username"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        this_user = db.query(User).filter(User.user_id == user_id).first()
        return this_user.id

def update_user_complites(id_us: int, complites: str):
    """Добавляет в поле complites выаолненые задания"""
    with Session(autoflush=False, bind=engine) as db:
        data_user = db.query(User).filter(User.id==id_us).first()
        if data_user != None:
            data_user.complite_tasks += f"{complites}, "
            db.commit()
            return f"{data_user.user_id}; {data_user.complite_tasks}"
        
def delete_user(id):
    """Удаляет пользователя по id"""
    with Session(autoflush=False, bind=engine) as db:
        user_for_delete = db.query(User).filter(User.id==id).first()
        db.delete(user_for_delete)
        db.commit()
        return "Чел успешно удалён"

def complites_use(user_id):
    """Возвращает все выполненые задания пользователя по username"""
    with Session(autoflush=False, bind=engine) as db:
        user_id = user_id.lower()
        user_cmp = db.query(User).filter(User.user_id==user_id).first()
        return user_cmp.complite_tasks

def complites_id(id):
    """Возвращает все выполненые задания пользователя по id"""
    return select_one_user_from_id(id).split(";")[1][:-2].replace(" ", "").split(",")

def is_admin(user_id: str):
    """Поверяет админ ли пользователь"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        check_user = db.query(User).filter(User.user_id==user_id).first()
        return True if check_user.admin == True else False

def user_page_number(user_id: str):
    """Возвращает номер страницы таксов человека"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        user_number = db.query(User).filter(User.user_id==user_id).first()
        return user_number.page_number
    
def next_page(user_id: str):
    """Отправляет пользователя на следующую старницу"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        data_user = db.query(User).filter(User.user_id==user_id).first()
        if data_user != None:
            data_user.page_number += 1
            db.commit()
            return data_user.page_number
        
def pre_page(user_id: str):
    """Отправляет пользователя на предыдущую страницу"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        data_user = db.query(User).filter(User.user_id==user_id).first()
        if data_user != None:
            data_user.page_number -= 1
            db.commit()
            return data_user.page_number
        
def is_complite(user_id: str, task_id: int):
    """Проверяет выполненно ли задание у пользователя"""
    user_id = user_id.lower()
    return True if str(task_id) in complites_use(user_id) else False

def add_admin(user_id: str):
    """Добавляет пользователю True в поле admin"""
    user_id = user_id.lower()
    with Session(autoflush=False, bind=engine) as db:
        new_admin = db.query(User).filter(User.user_id==user_id).first()
        if new_admin != None:
            new_admin.admin = True
            db.commit()
            return "Админ добавлен"
        else: return "Такого пользователя нет"