from flask import Flask, request, redirect, render_template_string, flash, url_for
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "segredo123"

POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiZmJhNTI5NGUtOTg1Ni00YWQ4LThkMDEtZmNlNGRjODA2Nzk5IiwidCI6IjNmOTU2NGZlLWQ3MjYtNGRmYS04NGY0LWI2ODVkNGM4ZGNmMiJ9"

USERS_FILE = "usuarios.csv"
LOG_FILE = "acessos.csv"


# ========== GESTÃO DE UTILIZADORES ==========

def init_users():
    """Cria o arquivo de usuários com João aprovado, caso não exista."""
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["João Bonfatti", "38172118", "1"])


def carregar_usuarios():
    """Carrega os usuários do CSV."""
    init_users()
    usuarios = {}
    with open(USERS_FILE, newline="", encoding="utf-8") as f:
        for nome, senha, aprovado in csv.reader(f, delimiter=";"):
            usuarios[nome] = (senha, aprovado == "1")
    return usuarios


def salvar_usuario(nome, senha):
    """Salva novo usuário como não aprovado."""
    with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=";").writerow([nome, senha, "0"])



# ========== CSS ==========

BASE_CSS = """
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #047444;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: Arial, sans-serif;
  }

  .card {
    background: white;
    padding: 30px;
    border-radius: 15px;
    width: 360px;
    text-align: center;
    box-shadow: 0 12px 25px rgba(0,0,0,0.25);
  }

  .logo {
    width: 90px;
    margin-bottom: 10px;
  }

  h1 {
    color: #047444;
    font-size: 20px;
    margin-bottom: 5px;
  }

  p.subtitulo {
    color: #666;
    font-size: 13px;
    margin-bottom: 20px;
  }

  label {
    display: block;
    text-align: left;
    margin-top: 10px;
    font-size: 14px;
    color: #333;
  }

  input {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    margin-top: 4px;
  }

  .btn-primary {
    width: 100%;
    background: #047444;
    border: none;
    padding: 12px;
    border-radius: 8px;
    margin-top: 18px;
    font-size: 15px;
    color: white;
    cursor: pointer;
    font-weight: bold;
  }

  .btn-secondary {
    width: 100%;
    background: white;
    border: 2px solid #047444;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
    font-size: 14px;
    color: #047444;
    cursor: pointer;
    font-weight: bold;
  }

  .mensagens p {
    color: red;
    font-size: 13px;
  }
</style>
"""



# ========== TELAS HTML ==========

LOGIN_HTML = BASE_CSS + """
<div class="card">
  <img src="{{ url_for('static', filename='america.png') }}" class="logo">
  <h1>Acesse os relatórios do América Futebol Clube</h1>
  <p class="subtitulo">Insira seu login e senha para continuar.</p>

  <div class="mensagens">
    {% for m in get_flashed_messages() %}
      <p>{{ m }}</p>
    {% endfor %}
  </div>

  <form method="POST">
    <label>Login</label>
    <input name="username" type="text">

    <label>Senha</label>
    <input name="password" type="password">

    <button class="btn-primary" type="submit">Entrar</button>
  </form>

  <button class="btn-secondary" onclick="window.location.href='/register'">Criar conta</button>
</div>
"""



REGISTER_HTML = BASE_CSS + """
<div class="card">
  <img src="{{ url_for('static', filename='america.png') }}" class="logo">
  <h1>Solicitar acesso</h1>
  <p class="subtitulo">Preencha os dados para criar seu cadastro.</p>

  <div class="mensagens">
    {% for m in get_flashed_messages() %}
      <p>{{ m }}</p>
    {% endfor %}
  </div>

  <form method="POST">
    <label>Login desejado</label>
    <input name="username" type="text">

    <label>Senha desejada</label>
    <input name="password" type="password">

    <button class="btn-primary" type="submit">Enviar solicitação</button>
  </form>

  <button class="btn-secondary" onclick="window.location.href='/'">Voltar</button>
</div>
"""



# ========== ROTAS ==========

@app.route("/", methods=["GET", "POST"])
def login():
    usuarios = carregar_usuarios()

    if request.method == "POST":
        nome = request.form["username"]
        senha = request.form["password"]

        if nome not in usuarios:
            flash("Usuário não encontrado.")
            return render_template_string(LOGIN_HTML)

        senha_real, aprovado = usuarios[nome]

        if senha != senha_real:
            flash("Senha incorreta.")
            return render_template_string(LOGIN_HTML)

        if not aprovado:
            flash("Seu acesso ainda não foi aprovado.")
            return render_template_string(LOGIN_HTML)

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f, delimiter=";").writerow([datetime.now(), nome])

        return redirect(POWERBI_URL)

    return render_template_string(LOGIN_HTML)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["username"]
        senha = request.form["password"]

        if not nome or not senha:
            flash("Preencha todos os campos.")
            return render_template_string(REGISTER_HTML)

        usuarios = carregar_usuarios()

        if nome in usuarios:
            flash("Este usuário já existe.")
            return render_template_string(REGISTER_HTML)

        salvar_usuario(nome, senha)
        flash("Solicitação enviada! Aguarde aprovação.")
        return render_template_string(LOGIN_HTML)

    return render_template_string(REGISTER_HTML)



# ========== INICIAR SISTEMA ==========

if __name__ == "__main__":
    init_users()
    app.run(debug=True)
