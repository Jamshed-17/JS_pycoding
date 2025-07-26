import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import json

from  js.task_compliter import test_solution
from database.crud import update_user_complites, select_one_user_from_id, select_one_user_from_use

tasks = json.load(open("data/tasks.json"))["tasks"]

def task_info(task_id: int):
    this_task = tasks[task_id-1]
    ret_str = f"**{this_task["name"]}**\n\n{this_task["description"]}.\nНазовите функцию {this_task["function_name"]}. Пример: ```js\n{this_task["template"]}\n```\nДанные для примера: ```json {this_task["fixed_tests"]}```"
    return [ret_str, this_task]

def task_trying(task_id: int, task_user_code: str, user_id: str):
    user_id = user_id.lower()
    solution = test_solution(task_id, task_user_code)
    if solution[0] == True:
        update_user_complites(select_one_user_from_use(user_id), f"{task_id}")

    return True if solution[0] == True else solution[1]

