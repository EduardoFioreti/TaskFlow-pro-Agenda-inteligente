import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuração simples: ele já sabe procurar as pastas 'templates' e 'static' ao lado dele
app = Flask(__name__)

# Configuração de caminhos do Banco
if os.environ.get('VERCEL'):
    db_path = '/tmp/agenda.db'
else:
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'agenda.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ... (restante dos modelos e rotas permanecem iguais) ...

# No final do arquivo, mantenha:
app = app

if __name__ == '__main__':
    app.run(debug=True)