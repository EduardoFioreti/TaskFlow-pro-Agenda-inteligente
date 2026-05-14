import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'),
            static_url_path='/static')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Se estiver na Vercel, o banco precisa ir para a pasta /tmp/ (única que aceita escrita)
if os.environ.get('VERCEL'):
    db_path = '/tmp/agenda.db'
else:
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'agenda.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def index():
    # Captura os parâmetros de filtro e busca da URL
    filtro_cat = request.args.get('filtrar_categoria')
    filtro_data = request.args.get('filtrar_data')
    busca = request.args.get('q')

    query = Tarefa.query

    # Lógica de Filtros
    if filtro_cat and filtro_cat != 'Todas':
        query = query.filter_by(categoria_nome=filtro_cat)
    if filtro_data:
        query = query.filter_by(data_evento=filtro_data)
    if busca:
        query = query.filter(Tarefa.descricao.contains(busca))

    # Ordenação: Pendentes primeiro, depois por data e hora
    tarefas = query.order_by(Tarefa.concluida, Tarefa.data_evento, Tarefa.hora_evento).all()
    categorias = Categoria.query.order_by(Categoria.nome).all() 

    return render_template('index.html', tarefas=tarefas, categorias=categorias)

@app.route('/add', methods=['POST'])
def add():
    descricao = request.form.get('descricao')
    data_str = request.form.get('data')
    hora_str = request.form.get('hora')
    categoria = request.form.get('categoria')
    
    if descricao and data_str and hora_str:
        try:
            # Validação simples: não permite datas passadas
            agora = datetime.now()
            data_usuario = datetime.strptime(f"{data_str} {hora_str}", '%Y-%m-%d %H:%M')
            
            if data_usuario >= agora:
                nova_tarefa = Tarefa(
                    descricao=descricao, 
                    data_evento=data_str, 
                    hora_evento=hora_str,
                    categoria_nome=categoria if categoria else 'Geral'
                )
                db.session.add(nova_tarefa)
                db.session.commit()
        except Exception as e:
            print(f"Erro ao adicionar: {e}")
            
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

# --- ROTAS DE CATEGORIA ---

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

# --- INICIALIZAÇÃO ---

with app.app_context():
    db.create_all()

# Export para a Vercel localizar o objeto do servidor
app = app

if __name__ == '__main__':
    app.run(debug=True)