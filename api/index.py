import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Agora o arquivo está na mesma altura das pastas static e templates
app = Flask(__name__, template_folder='templates', static_folder='static')

# Banco de dados
if os.environ.get('VERCEL'):
    db_path = '/tmp/agenda.db'
else:
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'agenda.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ... (resto do seu código de modelos e rotas continua igual) ...

# No final do arquivo, mude o app_handler para:
app = app