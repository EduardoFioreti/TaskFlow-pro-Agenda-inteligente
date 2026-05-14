import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Como está na raiz, o Flask encontrará as pastas 'templates' e 'static' automaticamente
app = Flask(__name__)

# Configuração do Banco de Dados
if os.environ.get('VERCEL'):
    db_path = '/tmp/agenda.db'
else:
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'agenda.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ... (seus modelos e rotas aqui) ...

with app.app_context():
    db.create_all()

# ESSENCIAL PARA A VERCEL:
app = app 

if __name__ == '__main__':
    app.run(debug=True)