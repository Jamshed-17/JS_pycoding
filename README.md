Этот небольшой, но интересный бот - это микро версия CodeWars, в котором есть несколько задач по JS.
Бот умеет заускать, проверять и отправлять информацию об ошибках.
Для работы этого бота в вашей среде вам нужно:

1. В `config.py` записать:
```
TOKEN="токен вашего телеграм бота"
TASKS_PATH="data/tasks.json" или другой путь
```
2. В этот самый `tasks.json` добавить данные вида:
```json
{
  "tasks": [
    {
      "id": 1,
      "name": "Сумма двух чисел",
      "function_name": "sum",
      "description": "Напишите функцию sum(a, b), которая возвращает сумму двух чисел",
      "level": 1,
      "fixed_tests": [
        {"input": [2, 3], "output": 5},
        {"input": [-1, 1], "output": 0}
      ],
      "random_test_generator": "function generateTest() {\n  const a = Math.floor(Math.random() * 200) - 100;\n  const b = Math.floor(Math.random() * 200) - 100;\n  return { input: [a, b], output: a + b };\n}",
      "template": "function sum(a, b) {\n  // Ваш код здесь\n}"
    },
    {
      "id": 2,
      "name": "Факториал",
      "function_name": "factorial",
      "description": "Напишите функцию factorial(n), которая возвращает факториал числа n",
      "level": 3,
      "fixed_tests": [
        {"input": [5], "output": 120},
        {"input": [0], "output": 1},
        {"input": [1], "output": 1}
      ],
      "random_test_generator": "function generateTest() {\n  const n = Math.floor(Math.random() * 10);\n  let output = 1;\n  for (let i = 2; i <= n; i++) output *= i;\n  return { input: [n], output: output };\n}",
      "template": "function factorial(n) {\n  // Ваш код здесь\n}"
    },
    ...
```

3. Для деплоя нужно
`git clone https://github.com/Jamshed-17/JS_pycoding.git`
`cd JS_pycoding`
`docker compose build --no-cache`
`docker compose up -d`

Ну и ... всё