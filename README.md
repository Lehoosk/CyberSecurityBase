# CyberSecurityBase
This repository is for Cyber Security Base Project I.  
It is a translation of a project made in the course TKT20019 Databases and Web Programming.  
The project was originally made using Flask, and now it is translated to Django, and it contains five security vulnerabilities on purpose.  

It is a very simple fitness application. Users can register, log in, and keep track of their exercises.  

## How to Run

1. Download all repository files into the same folder. If you downloaded them as a zip, extract the files first.  

2. Open the project folder in Visual Studio Code

3. Create a virtual environment:  
   python -m venv venv

4. Activate the virtual environmetn:
.\venv\Scripts\Activate.ps1

5. Instal Django (if not already done)
   pip install django

6. Run the application
   python manage.py runserver

7. Open a browser and go to: http://127.0.0.1:8000/

Note, the repository contains an example SQLite database (database.db) with a few rows of test data.
If you need to reset or modify database, you can use sqlite3.exe in the same folder.
The SQL schema is included as schema.sql and can be loaded into an empty database with:

  .\sqlite3.exe .\database.db ".read schema.sql"
In such case you also need to migrate Django system tables:
  python.exe .\manage.py migrate
