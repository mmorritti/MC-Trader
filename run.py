import backend.main_server
import backend.database as db
import backend.commands as cmd


while True:
    command = input()
    try:
        exec(compile(command, "command", "exec", optimize=1))
    except Exception as e:
        print(e)
