import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import json
import config
import natsort
import random

from js.task_compliter import test_solution
from database.crud import update_user_complites, select_one_user_from_id, select_one_user_from_use, complites_use

tasks = json.load(open(config.TASKS_PATH))["tasks"]

def task_info(task_id: int):
    this_task = tasks[task_id-1]
    ret_str = f"**{this_task['name']}** (level {this_task['level']})\n\n{this_task['description']}.\nНазовите функцию {this_task['function_name']}. Пример: ```js\n{this_task['template']}\n```\nДанные для примера: ```json {this_task['fixed_tests']}```"
    return [ret_str, this_task]

def task_trying(task_id: int, task_user_code: str, user_id: str):
    user_id = user_id.lower()
    solution = test_solution(task_id, task_user_code)
    if solution[0] == True:
        update_user_complites(select_one_user_from_use(user_id), f"{task_id}")
    return True if solution[0] == True else solution[1]

def complite_tasks(user_id: str):
    completed_ids = [int(i) for i in complites_use(user_id).replace(" ", "").split(",") if i]
    unique_sorted_ids = sorted(set(completed_ids))
    
    total_completed = len(unique_sorted_ids)
    total_tasks = len(tasks)
    progress_percent = int((total_completed / total_tasks) * 100)
    filled = progress_percent // 5
    progress_bar = "▓" * filled + "░" * (20 - filled)
    
    icons = ["🧩", "🔠", "🔢", "🔄", "✨", "✅", "🏆", "💡", "📌", "🎯", "🧠", "⚡️", "🔍", "📊", "🎲"]
    
    task_lines = []
    for task_id in unique_sorted_ids:
        task = tasks[task_id-1]
        icon = random.choice(icons)
        task_lines.append(f"• {icon} {task['name']} [#{task['id']}]")
    
    return f"""
✅ *Твой прогресс:*
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
 {progress_bar} {progress_percent}% 
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Решённые задачи:
{chr(10).join(task_lines)}

Молодец! Продолжай в том же духе! 💪
"""
