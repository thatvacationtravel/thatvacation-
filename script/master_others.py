import subprocess


manage_py_directory = "/home/tvacation/thatvacation"


commands = [
    "manage.py importar_puertos /home/tvacation/thatvacation/json_others/flatportdetl_eng.csv",
]

def run_django_command(command):
    try:
        print(f"Ejecutando {command}...")
        result = subprocess.run(
            ["python3"] + command.split(),
            check=True,
            capture_output=True,
            text=True,
            cwd=manage_py_directory
        )
        print(f"Salida de {command}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {command}:\n{e.stderr}")
        exit(1)


for command in commands:
    run_django_command(command)

print("Todos los comandos de Django se han ejecutado.")
