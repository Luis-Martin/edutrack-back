# Edutrack Back

Pasos para correr la API

1. Clonar el repositorio
    ```powershell
    git clone git@github.com:Luis-Martin/edutrack-back.git
    cd edutrack-back
    ```

2.  Crear el entorno virtual
    ```powershell
    python -m venv venv
    ```

3. Activar el entorno virtual 
    ```powershell
    .\venv\Scripts\activate
    ```

4. Instalar los paquetes
    ```powershell
    pip install -r requirements.txt
    ```

5. Migrar las bbdd
    ```powershell
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Correr la app
    ```powershell
    python manage.py runserver
    ```