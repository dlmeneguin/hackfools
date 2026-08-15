import json
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "chave super secreta"


def get_db():
    db = sqlite3.connect("banco.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    return db, cursor

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        db, cursor = get_db()
        data = request.form
        usuario, senha, confirmacao = data['usuario'], data['senha'], data['confirmacao']

        print(usuario, senha, confirmacao)

        #verificação de input e db
        if usuario == '' or senha == '' or confirmacao == '':
            db.close()
            return render_template("signin.html", erro="Preencha todos os campos")

        cursor.execute("SELECT * FROM pessoas WHERE usuario=?", [usuario])
        verificacao = cursor.fetchone()
        if verificacao != None:
            db.close()
            return render_template("signin.html", erro="Já existe um usuario com este nome")
        if senha != confirmacao:
            db.close()
            return render_template("signin.html", erro="As senhas não batem")
        
        #adição do usuario ao banco de dados e redirecionamento
        cursor.execute("INSERT INTO pessoas (usuario, senha) VALUES (?, ?)", [usuario, senha])
        session['login'] = usuario
        db.commit()
        db.close()
        return redirect(url_for('user', word=usuario))
    return render_template("signin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db, cursor = get_db()
        data = request.form
        usuario, senha = data['usuario'], data['senha']

        print(usuario, senha)

        #verificação de input e db
        if usuario == '' or senha == '':
            db.close()
            return render_template("login.html", erro="Preencha todos os campos")

        cursor.execute("SELECT * FROM pessoas WHERE usuario=? AND senha=?", [usuario, senha])
        verificacao = cursor.fetchone()

        # usuario nao existe
        if verificacao == None:
            db.close()
            return render_template("login.html", erro="Usuario não existe")

        # faz login
        db.close()
        session['login'] = usuario
        return redirect(url_for('user', word=usuario))

    return render_template("login.html")


@app.route('/user/<word>', methods=['GET', 'POST'])
def user(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('user', word=session['login']))

    db, cursor = get_db()
    cursor.execute("SELECT * FROM pessoas WHERE usuario=?", [word])
    verificacao = cursor.fetchone()
    db.close()
    if verificacao == None:
        session.clear()
        return redirect(url_for('login'))

    return render_template("dentro.html", word=word)


@app.route('/user/<word>/editor', methods=['GET', 'POST'])
def editor(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('editor', word=session['login']))
    return render_template("editor.html", word=word)


@app.route('/user/<word>/marketplace', methods=['GET', 'POST'])
def marketplace(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('marketplace', word=session['login']))

    db, cursor = get_db()
    cursor.execute(
        "SELECT id, usuario, nome, categoria, raridade, preco FROM marketplace_items ORDER BY id DESC"
    )
    rows = cursor.fetchall()

    db.close()

    listings = [
        {
            "id": row["id"],
            "seller": row["usuario"],
            "name": row["nome"],
            "category": row["categoria"],
            "rarity": row["raridade"],
            "price": row["preco"],
        }
        for row in rows
    ]

    listings_json = json.dumps(listings)

    print(listings_json)

    return render_template("marketplace.html", word=word, listings=listings, listings_json=listings_json)


@app.route('/user/<word>/perfil', methods=['GET', 'POST'])
def perfil(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('perfil', word=session['login']))

    if request.method == "POST":
        nome = request.form.get("nome")
        categoria = request.form.get("categoria")
        raridade = request.form.get("raridade")
        preco = request.form.get("preco")

        if nome and categoria and raridade and preco:
            try:
                preco_int = int(preco)
                db, cursor = get_db()
                cursor.execute(
                    "INSERT INTO marketplace_items (usuario, nome, categoria, raridade, preco) VALUES (?, ?, ?, ?, ?)",
                    [word, nome, categoria, raridade, preco_int]
                )
                db.commit()
                db.close()
                flash("Anúncio criado com sucesso!")
                return redirect(url_for('marketplace', word=word))
            except Exception as e:
                print(e)
                if 'db' in locals():
                    db.close()
                flash("Erro ao criar anúncio.")

    return render_template("perfil.html", word=word)


@app.route('/user/<word>/lootbox', methods=['GET', 'POST'])
def lootboxes(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('lootboxes', word=session['login']))
    return render_template("lootbox.html", word=word)


@app.route("/logout")
def logout():
    db, cursor = get_db()
    db.close()
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
