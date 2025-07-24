import json
import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import TASKS_PATH

def run_js(code):
    """Запускает JS-код в Node.js и возвращает stdout"""
    result = subprocess.run(
        ['node', '-e', code],
        capture_output=True,
        text=True,
        timeout=2  # Защита от бесконечных циклов
    )
    if result.stderr:
        return f"ERROR: {result.stderr.strip()}"
    return result.stdout.strip()

def test_solution(task_id, user_code):
    """Тестирует решение пользователя"""
    with open(TASKS_PATH) as f:
        tasks = json.load(f)['tasks']
    
    task = next(t for t in tasks if t['id'] == task_id)
    func_name = task['function_name']  # Получаем имя функции из JSON

    # Проверяем фиксированные тесты
    for test in task['fixed_tests']:
        js_code = f"""
            {user_code}
            const result = {func_name}(...{json.dumps(test['input'])});
            console.log(JSON.stringify(result));
        """
        expected = json.dumps(test['output'])
        actual = run_js(js_code)

        if actual != expected:
            return [False, f"❌ Тест провален: {test['input']} -> Ожидалось {expected}, получено {actual}"]

    # Проверяем рандомные тесты (3 раза)
    for _ in range(3):
        gen_code = f"{task['random_test_generator']}\nconsole.log(JSON.stringify(generateTest()))"
        test = json.loads(run_js(gen_code))

        js_code = f"""
            {user_code}
            const result = {func_name}(...{json.dumps(test['input'])});
            console.log(JSON.stringify(result));
        """
        expected = json.dumps(test['output'])
        actual = run_js(js_code)

        if actual != expected:
            return [False, f"❌ Рандомный тест провален: {test['input']} -> Ожидалось {expected}, получено {actual}"]

    return [True, "Все тесты пройдены"]

user_code = """
function sum(a, b) {
  return a + b;
}
"""
print(test_solution(1, user_code)) 