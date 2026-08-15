from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave super secreta"

def get_db():
    db = sqlite3.connect("banco.db")
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
        return redirect(f"user/{usuario}")
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
            return render_template("signin.html", erro="Preencha todos os campos")

        cursor.execute("SELECT * FROM pessoas WHERE usuario=? AND senha=?", [usuario, senha])
        verificacao = cursor.fetchone()

        # usuario nao existe
        if verificacao == None:
            db.close()
            return render_template("login.html", erro="Usuario não existe")

        # faz login
        db.close()
        session['login'] = usuario
        return redirect(f"user/{usuario}")

    return render_template("login.html")


@app.route('/user/<word>', methods=['GET', 'POST'])
def user(word):
        db, cursor = get_db()
        cursor.execute("SELECT * FROM pessoas WHERE usuario=?", [word])
        verificacao = cursor.fetchone()
        if verificacao == None:
            db.close()
            return redirect("/")
        try:
            temp = session['login']
        except:
            db.close()
            flash("Favor realize o log-in")
            return redirect(url_for('login'))
        if session['login'] == word:
            db.close()
            return render_template("dentro.html", word=word)

@app.route('/user/<word>/lootbox', methods=['GET', 'POST'])
def lootboxes(word):
    return render_template("lootbox.html", word=word)


@app.route("/logout")
def logout():
    db, cursor = get_db()
    db.close()
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
