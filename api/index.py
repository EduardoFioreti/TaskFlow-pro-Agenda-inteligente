import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. Configuração do App
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# 2. Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS ---

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    data_evento = db.Column(db.String(10), nullable=False)
    hora_evento = db.Column(db.String(5), nullable=False) 
    categoria_nome = db.Column(db.String(50), nullable=False)
    concluida = db.Column(db.Boolean, default=False)

# --- ROTAS ---

@app.route('/')
def index():
    # Captura filtros, busca e data da URL
    filtro_cat = request.args.get('filtrar_categoria')
    filtro_data = request.args.get('filtrar_data')
    busca = request.args.get('q') # Barra de pesquisa

    query = Tarefa.query

    # Filtro por Categoria
    if filtro_cat and filtro_cat != 'Todas':
        query = query.filter_by(categoria_nome=filtro_cat)
    
    # Filtro por Data
    if filtro_data:
        query = query.filter_by(data_evento=filtro_data)
        
    # Busca por Texto (Descricao)
    if busca:
        query = query.filter(Tarefa.descricao.contains(busca))

    # ORDENAÇÃO INTELIGENTE: 
    # 1º: Tarefas pendentes primeiro (concluida=False/0 vem antes de True/1)
    # 2º: Data e Hora
    tarefas = query.order_by(Tarefa.concluida, Tarefa.data_evento, Tarefa.hora_evento).all()
    categorias = Categoria.query.order_by(Categoria.nome).all() 

    return render_template('index.html', tarefas=tarefas, categorias=categorias)

@app.route('/add_category', methods=['POST'])
def add_category():
    nome = request.form.get('nome_categoria', '').strip()
    if nome:
        nome = nome.capitalize()
        existe = Categoria.query.filter_by(nome=nome).first()
        if not existe:
            nova_cat = Categoria(nome=nome)
            db.session.add(nova_cat)
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_category/<int:id>')
def delete_category(id):
    cat = Categoria.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    descricao = request.form.get('descricao')
    data_str = request.form.get('data')
    hora_str = request.form.get('hora')
    categoria = request.form.get('categoria')
    
    if descricao and data_str and hora_str:
        try:
            agora = datetime.now()
            data_usuario = datetime.strptime(f"{data_str} {hora_str}", '%Y-%m-%d %H:%M')
            
            if data_usuario < agora:
                return redirect(url_for('index'))
            
            nova_tarefa = Tarefa(
                descricao=descricao, 
                data_evento=data_str, 
                hora_evento=hora_str,
                categoria_nome=categoria if categoria else 'Geral'
            )
            db.session.add(nova_tarefa)
            db.session.commit()
        except Exception as e:
            print(f"Erro: {e}")
            
    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
def complete(id):
    tarefa = Tarefa.query.get_or_404(id)
    tarefa.concluida = not tarefa.concluida
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('index'))

# Inicialização do Banco
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)