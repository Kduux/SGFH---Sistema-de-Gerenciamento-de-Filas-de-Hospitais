from functools import wraps
from conexao import get_conn
from flask import Flask, redirect, render_template, request, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'sgfh_hospital_secret_2025'

# ── Decorator de autenticação ──────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'funcionario_id' not in session:
            return redirect(url_for('pagina_login'))
        return f(*args, **kwargs)
    return decorated

# ── PARTE 1: Index ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── PARTE 2: Totem ─────────────────────────────────────────────────────────────
@app.route("/totem")
def pagina_totem():
    return render_template("totem.html")

@app.route("/gerar_senha", methods=["POST"])
def gerar_senha():
    data = request.get_json()
    tipo = data.get("tipo", "normal")
    prefix = 'P' if tipo == 'prioritario' else 'N'

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM senhas WHERE tipo = ?", (tipo,))
    count = cursor.fetchone()['total']
    valor = f"{prefix}{count + 1:03d}"

    cursor.execute(
        "INSERT INTO senhas (valor, tipo, status) VALUES (?, ?, 'aguardando')",
        (valor, tipo)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"senha": valor, "tipo": tipo})

# ── PARTE 3: Login / Guichê ────────────────────────────────────────────────────
@app.route("/login", methods=["GET"])
def pagina_login():
    if 'funcionario_id' in session:
        return redirect(url_for('pagina_guiche'))
    return render_template("login.html")

@app.route("/logar", methods=["POST"])
def logar():
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()

    if not email or not senha:
        return render_template("login.html", error="Preencha todos os campos.")

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM funcionarios WHERE email = ? AND senha = ?",
        (email, senha)
    )
    funcionario = cursor.fetchone()
    cursor.close()
    conn.close()

    if funcionario:
        session['funcionario_id']   = funcionario['id']
        session['funcionario_nome'] = funcionario['nome']
        session['guiche']           = funcionario['id']   # guichê = ID do funcionário
        return redirect(url_for('pagina_guiche'))
    else:
        return render_template("login.html", error="E-mail ou senha incorretos.")

@app.route("/guiche")
@login_required
def pagina_guiche():
    return render_template("controle.html",
                           nome=session['funcionario_nome'],
                           guiche=session['guiche'])

@app.route("/chamar_proximo", methods=["POST"])
@login_required
def chamar_proximo():
    guiche = session['guiche']

    conn = get_conn()
    cursor = conn.cursor()

    # Marca a senha atual deste guichê como atendida
    cursor.execute(
        "UPDATE senhas SET status='atendido' WHERE status='chamado' AND guiche=?",
        (guiche,)
    )

    # Busca a próxima: prioritário > normal, mais antiga primeiro
    cursor.execute(
        """SELECT * FROM senhas
           WHERE status='aguardando'
           ORDER BY tipo DESC, criado_em ASC
           LIMIT 1"""
    )
    proxima = cursor.fetchone()

    if proxima:
        cursor.execute(
            """UPDATE senhas
               SET status='chamado', guiche=?, chamado_em=CURRENT_TIMESTAMP
               WHERE id=?""",
            (guiche, proxima['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"senha": proxima['valor'], "guiche": guiche, "tipo": proxima['tipo']})
    else:
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"senha": None, "guiche": guiche, "mensagem": "Fila vazia"})

# ── PARTE 4: Painel de TV ──────────────────────────────────────────────────────
@app.route("/painel")
def pagina_painel():
    return render_template("painel.html")

@app.route("/api/painel")
def api_painel():
    conn = get_conn()
    cursor = conn.cursor()

    # Senha atualmente chamada (mais recente)
    cursor.execute(
        """SELECT * FROM senhas
           WHERE status='chamado'
           ORDER BY chamado_em DESC LIMIT 1"""
    )
    atual = cursor.fetchone()

    # Últimas 3 atendidas (histórico)
    cursor.execute(
        """SELECT * FROM senhas
           WHERE status='atendido'
           ORDER BY chamado_em DESC LIMIT 3"""
    )
    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "atual": {
            "valor":  atual['valor'],
            "guiche": atual['guiche'],
            "tipo":   atual['tipo']
        } if atual else None,
        "historico": [
            {"valor": s['valor'], "guiche": s['guiche']}
            for s in historico
        ]
    })

# ── Cadastro ───────────────────────────────────────────────────────────────────
@app.route("/cadastro", methods=["GET"])
def pagina_cadastro():
    return render_template("cadastro.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar_usuario():
    nome  = request.form.get("nome",  "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()

    if not nome or not email or not senha:
        return render_template("cadastro.html", error="Preencha todos os campos.")

    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO funcionarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email, senha)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return render_template("cadastro.html", success="Funcionário cadastrado com sucesso!")
    except Exception:
        return render_template("cadastro.html", error="E-mail já cadastrado.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('pagina_login'))

if __name__ == '__main__':
    app.run(debug=True)