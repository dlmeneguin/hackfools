import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "chave super secreta"


def get_db():
    db = sqlite3.connect("banco.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    return db, cursor


BOX_ITEMS = {
    'cabelo': [
        ('Liso fino — castanho', 'comum', 22),
        ('Liso grosso — preto', 'comum', 18),
        ('Ondulado — castanho claro', 'comum', 18),
        ('Cacheado — ruivo', 'incomum', 14),
        ('Crespo — preto profundo', 'incomum', 12),
        ('Ondulado — loiro dourado', 'raro', 8),
        ('Cacheado — ruivo intenso', 'epico', 5),
        ('Platinado natural', 'lendario', 3)
    ],
    'pele': [
        ('Clara — textura suave', 'comum', 20),
        ('Bege — poros finos', 'comum', 20),
        ('Morena — uniforme', 'comum', 20),
        ('Oliva — luminosa', 'incomum', 15),
        ('Escura — aveludada', 'incomum', 12),
        ('Ébano — profundo', 'raro', 8),
        ('Dourada — pigmentação rara', 'epico', 4),
        ('Translúcida perolada', 'lendario', 1)
    ],
    'olhos': [
        ('Castanho escuro', 'comum', 28),
        ('Castanho claro', 'comum', 18),
        ('Verde musgo', 'incomum', 14),
        ('Azul acinzentado', 'incomum', 14),
        ('Avelã misto', 'incomum', 12),
        ('Cinza claro', 'raro', 8),
        ('Âmbar', 'epico', 4),
        ('Heterocromia', 'lendario', 2)
    ],
    'boca': [
        ('Lábios finos — simétricos', 'comum', 25),
        ('Lábios médios — definidos', 'comum', 33),
        ('Lábios carnudos — naturais', 'incomum', 22),
        ('Assimetria natural — marcante', 'raro', 12),
        ('Sorriso excepcional', 'epico', 8)
    ],
    'nariz': [
        ('Reto — médio', 'comum', 25),
        ('Arredondado — suave', 'comum', 24),
        ('Aquilino — elegante', 'incomum', 20),
        ('Snub — delicado', 'incomum', 15),
        ('Reto — fino de perfil', 'raro', 10),
        ('Grego esculpido', 'epico', 6)
    ],
    'voz': [
        ('Médio neutro', 'comum', 25),
        ('Médio-grave — caloroso', 'comum', 22),
        ('Grave — encorpado', 'incomum', 18),
        ('Agudo — cristalino', 'incomum', 16),
        ('Grave profundo', 'raro', 10),
        ('Melodioso — amplo alcance', 'epico', 7),
        ('Voz excepcional — única', 'lendario', 2)
    ],
    'altura': [
        ('Baixa — abaixo de 160cm', 'comum', 12),
        ('Média-baixa — 160 a 170cm', 'comum', 20),
        ('Média — 170 a 180cm', 'comum', 30),
        ('Média-alta — 180 a 190cm', 'incomum', 22),
        ('Alta — 190 a 198cm', 'raro', 11),
        ('Excepcional — acima de 198cm', 'epico', 5)
    ],
    'inteligencia': [
        ('QI 90–100 — médio', 'comum', 22),
        ('QI 100–110 — médio-alto', 'comum', 28),
        ('QI 110–120 — alto', 'incomum', 22),
        ('QI 120–130 — muito alto', 'raro', 16),
        ('QI 130–140 — excepcional', 'epico', 8),
        ('QI 140+ — genial', 'lendario', 4)
    ],
    'carisma': [
        ('Reservado — introvertido', 'comum', 18),
        ('Amigável — sociável', 'comum', 28),
        ('Carismático — cativante', 'incomum', 24),
        ('Muito carismático — líder', 'raro', 16),
        ('Magnético — irresistível', 'epico', 10),
        ('Lendário — uma geração', 'lendario', 4)
    ],
    'atleticidade': [
        ('Base sedentária', 'comum', 12),
        ('Mediano — funcional', 'comum', 28),
        ('Atlético — acima da média', 'incomum', 28),
        ('Muito atlético — destacado', 'raro', 18),
        ('Elite — nível competitivo', 'epico', 10),
        ('Sobre-humano', 'lendario', 4)
    ],
    'imunologico': [
        ('Fraco — suscetível', 'comum', 8),
        ('Abaixo da média', 'comum', 14),
        ('Médio — funcional', 'comum', 30),
        ('Robusto — resistente', 'incomum', 26),
        ('Excepcional — raramente adoece', 'raro', 15),
        ('Imunidade avançada', 'epico', 7)
    ]
}


TRAIT_RARITY_MAP = {}
for category, items in BOX_ITEMS.items():
    for item in items:
        TRAIT_RARITY_MAP[item[0]] = item[1]


def init_db():
    db, cursor = get_db()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            creditos INTEGER DEFAULT 3000
        )
    """)
    
    cursor.execute("PRAGMA table_info(pessoas)")
    columns = [col[1] for col in cursor.fetchall()]
    if "creditos" not in columns:
        cursor.execute("ALTER TABLE pessoas ADD COLUMN creditos INTEGER DEFAULT 3000")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketplace_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            raridade TEXT NOT NULL,
            preco INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM marketplace_items")
    if cursor.fetchone()[0] == 0:
        dados_mockados = [
            ("Dr. Arthur", "Platinado natural", "cabelo", "lendario", 1500),
            ("Dra. Elena", "Heterocromia", "olhos", "lendario", 1800),
            ("Alex_Genetics", "Inteligência Excepcional", "inteligencia", "epico", 950),
            ("Sérgio_V", "Sorriso excepcional", "boca", "epico", 800),
            ("BioTrader", "Azul acinzentado", "olhos", "incomum", 300),
            ("Luna_M", "Atleticidade Elevada", "atleticidade", "raro", 550),
            ("Carlos_H", "Clara — textura suave", "pele", "comum", 100),
            ("Ana_Gen", "Crespo — preto profundo", "cabelo", "incomum", 250),
        ]
        cursor.executemany(
            "INSERT INTO marketplace_items (usuario, nome, categoria, raridade, preco) VALUES (?, ?, ?, ?, ?)",
            dados_mockados,
        )

    db.commit()
    db.close()


init_db()


def check_and_seed_inventory(username):
    db, cursor = get_db()
    cursor.execute("SELECT id FROM pessoas WHERE usuario=?", [username])
    user_row = cursor.fetchone()
    if not user_row:
        db.close()
        return
    user_id = user_row["id"]

    cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario=?", [user_id])
    count = cursor.fetchone()[0]
    if count == 0:
        initial_items = [
            ("Ondulado — loiro dourado", "cabelo"),
            ("Oliva — luminosa", "pele"),
            ("Cinza claro", "olhos"),
            ("Lábios carnudos — naturais", "boca"),
            ("Reto — fino de perfil", "nariz"),
            ("Grave profundo", "voz"),
            ("Média-alta — 180 a 190cm", "altura"),
            ("QI 120–130 — muito alto", "inteligencia"),
            ("Muito carismático — líder", "carisma"),
            ("Muito atlético — destacado", "atleticidade"),
            ("Excepcional — raramente adoece", "imunologico")
        ]
        cursor.executemany(
            "INSERT INTO inventario (id_usuario, nome, tipo) VALUES (?, ?, ?)",
            [(user_id, item[0], item[1]) for item in initial_items]
        )
        db.commit()
    db.close()


def get_user_credits(username):
    db, cursor = get_db()
    cursor.execute("SELECT creditos FROM pessoas WHERE usuario=?", [username])
    row = cursor.fetchone()
    db.close()
    if row:
        return row["creditos"]
    return 3000


import random

def pick_lootbox_item(category):
    items = BOX_ITEMS.get(category, [])
    if not items:
        return None
    names_rarities = [(item[0], item[1]) for item in items]
    weights = [item[2] for item in items]
    choice = random.choices(names_rarities, weights=weights, k=1)[0]
    return {"name": choice[0], "rarity": choice[1], "category": category}

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
        cursor.execute("INSERT INTO pessoas (usuario, senha, creditos) VALUES (?, ?, 3000)", [usuario, senha])
        session['login'] = usuario
        db.commit()
        db.close()
        check_and_seed_inventory(usuario)
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

    check_and_seed_inventory(word)
    creditos = get_user_credits(word)

    db, cursor = get_db()
    cursor.execute("SELECT * FROM pessoas WHERE usuario=?", [word])
    verificacao = cursor.fetchone()
    if verificacao == None:
        db.close()
        session.clear()
        return redirect(url_for('login'))
        
    cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario=?", [verificacao["id"]])
    traits_ativos = cursor.fetchone()[0]
    db.close()

    return render_template("dentro.html", word=word, creditos=creditos, traits_ativos=traits_ativos)


def get_grouped_inventory(username):
    check_and_seed_inventory(username)
    db, cursor = get_db()
    cursor.execute("SELECT id FROM pessoas WHERE usuario=?", [username])
    user_row = cursor.fetchone()
    if not user_row:
        db.close()
        return {}
    user_id = user_row["id"]
    
    cursor.execute("SELECT nome, tipo FROM inventario WHERE id_usuario=?", [user_id])
    rows = cursor.fetchall()
    db.close()
    
    inventory = {}
    for row in rows:
        cat = row["tipo"]
        if cat not in inventory:
            inventory[cat] = []
        rarity = TRAIT_RARITY_MAP.get(row["nome"], "comum")
        inventory[cat].append({
            "name": row["nome"],
            "rarity": rarity
        })
    return inventory


@app.route('/user/<word>/editor', methods=['GET', 'POST'])
def editor(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('editor', word=session['login']))
    
    inventory = get_grouped_inventory(word)
    creditos = get_user_credits(word)
    return render_template("editor.html", word=word, inventory=inventory, creditos=creditos)


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

    creditos = get_user_credits(word)
    return render_template("marketplace.html", word=word, listings=listings, creditos=creditos)


@app.route('/user/<word>/marketplace/buy', methods=['POST'])
def buy_marketplace_item(word):
    if 'login' not in session or session['login'] != word:
        return {"success": False, "message": "Não autorizado"}, 403

    item_id = request.form.get("item_id")
    if not item_id:
        return {"success": False, "message": "ID do item faltando"}, 400

    db, cursor = get_db()
    cursor.execute("SELECT usuario, nome, categoria, raridade, preco FROM marketplace_items WHERE id=?", [item_id])
    item = cursor.fetchone()
    if not item:
        db.close()
        return {"success": False, "message": "Item não encontrado no marketplace"}, 404

    seller, nome, categoria, raridade, preco = item["usuario"], item["nome"], item["categoria"], item["raridade"], item["preco"]

    if seller == word:
        db.close()
        return {"success": False, "message": "Você não pode comprar seu próprio item"}, 400

    cursor.execute("SELECT creditos FROM pessoas WHERE usuario=?", [word])
    buyer_row = cursor.fetchone()
    if not buyer_row or buyer_row["creditos"] < preco:
        db.close()
        return {"success": False, "message": "Créditos insuficientes"}, 400

    buyer_credits = buyer_row["creditos"]

    try:
        cursor.execute("UPDATE pessoas SET creditos = creditos - ? WHERE usuario=?", [preco, word])
        seller_receive = int(preco * 0.95)
        cursor.execute("UPDATE pessoas SET creditos = creditos + ? WHERE usuario=?", [seller_receive, seller])
        cursor.execute("DELETE FROM marketplace_items WHERE id=?", [item_id])
        cursor.execute("INSERT INTO inventario (id_usuario, nome, tipo) VALUES ((SELECT id FROM pessoas WHERE usuario=?), ?, ?)",
                       [word, nome, categoria])
        db.commit()
        db.close()
        return {"success": True, "message": "Compra realizada com sucesso!", "new_balance": buyer_credits - preco}
    except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return {"success": False, "message": "Erro processando a transação"}, 500


def get_user_inventory(username):
    check_and_seed_inventory(username)
    db, cursor = get_db()
    cursor.execute("SELECT id FROM pessoas WHERE usuario=?", [username])
    user_row = cursor.fetchone()
    if not user_row:
        db.close()
        return []
    user_id = user_row["id"]

    cursor.execute("SELECT nome, tipo FROM inventario WHERE id_usuario=?", [user_id])
    rows = cursor.fetchall()
    db.close()

    cosmetic_cats = ["cabelo", "pele", "olhos", "boca", "nariz", "voz"]
    category_display_names = {
        "cabelo": "Cabelo",
        "pele": "Pele",
        "olhos": "Olhos",
        "boca": "Boca",
        "nariz": "Nariz",
        "voz": "Voz",
        "altura": "Altura",
        "inteligencia": "Inteligência",
        "carisma": "Carisma",
        "atleticidade": "Atleticidade",
        "imunologico": "Sist. Imunológico"
    }

    inventory = []
    for row in rows:
        cat = row["tipo"].lower()
        item_type = "cosmetico" if cat in cosmetic_cats else "atributo"
        rarity = TRAIT_RARITY_MAP.get(row["nome"], "comum")
        inventory.append({
            "name": row["nome"],
            "category": category_display_names.get(cat, row["tipo"]),
            "type": item_type,
            "rarity": rarity
        })
    return inventory


@app.route('/user/<word>/perfil', methods=['GET', 'POST'])
def perfil(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('perfil', word=session['login']))

    if request.method == "POST":
        nome = request.form.get("nome")
        categoria_display = request.form.get("categoria")
        raridade = request.form.get("raridade")
        preco = request.form.get("preco")

        # Map display name to category ID in DB
        category_map = {
            "Cabelo": "cabelo",
            "Pele": "pele",
            "Olhos": "olhos",
            "Boca": "boca",
            "Nariz": "nariz",
            "Voz": "voz",
            "Altura": "altura",
            "Inteligência": "inteligencia",
            "Carisma": "carisma",
            "Atleticidade": "atleticidade",
            "Sist. Imunológico": "imunologico"
        }
        categoria = category_map.get(categoria_display, categoria_display.lower())

        if nome and categoria and raridade and preco:
            try:
                preco_int = int(preco)
                db, cursor = get_db()
                # 1. Remove from user inventory (limit 1)
                cursor.execute(
                    "DELETE FROM inventario WHERE id = (SELECT id FROM inventario WHERE id_usuario=(SELECT id FROM pessoas WHERE usuario=?) AND nome=? AND tipo=? LIMIT 1)",
                    [word, nome, categoria]
                )
                # 2. Add to marketplace items
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

    inventory = get_user_inventory(word)
    creditos = get_user_credits(word)
    return render_template("perfil.html", word=word, inventory=inventory, creditos=creditos)


@app.route('/user/<word>/lootbox', methods=['GET', 'POST'])
def lootboxes(word):
    if 'login' not in session:
        flash("Favor realize o log-in")
        return redirect(url_for('login'))
    if session['login'] != word:
        return redirect(url_for('lootboxes', word=session['login']))
    
    creditos = get_user_credits(word)
    return render_template("lootbox.html", word=word, creditos=creditos)


@app.route('/user/<word>/lootbox/open', methods=['POST'])
def open_lootbox(word):
    if 'login' not in session or session['login'] != word:
        return {"success": False, "message": "Não autorizado"}, 403

    category = request.form.get("category")
    if not category:
        return {"success": False, "message": "Categoria faltando"}, 400

    box_cost = 300

    db, cursor = get_db()
    cursor.execute("SELECT creditos FROM pessoas WHERE usuario=?", [word])
    user_row = cursor.fetchone()
    if not user_row or user_row["creditos"] < box_cost:
        db.close()
        return {"success": False, "message": f"Créditos insuficientes ({box_cost} CR necessários)"}, 400

    buyer_credits = user_row["creditos"]

    item = pick_lootbox_item(category)
    if not item:
        db.close()
        return {"success": False, "message": "Categoria inválida"}, 400

    try:
        cursor.execute("UPDATE pessoas SET creditos = creditos - ? WHERE usuario=?", [box_cost, word])
        cursor.execute(
            "INSERT INTO inventario (id_usuario, nome, tipo) VALUES ((SELECT id FROM pessoas WHERE usuario=?), ?, ?)",
            [word, item["name"], item["category"]]
        )
        db.commit()
        db.close()
        return {
            "success": True,
            "message": "Caixa aberta com sucesso!",
            "item": item,
            "new_balance": buyer_credits - box_cost
        }
    except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return {"success": False, "message": "Erro ao processar abertura"}, 500


@app.route('/injecao', methods=['GET', 'POST'])
def injecao():
    usuario = request.args.get('usuario')
    quantidade = request.args.get('quantidade')

    if not usuario or not quantidade:
        return "Uso correto: /injecao?usuario=NOME&quantidade=VALOR", 400

    try:
        quantidade_int = int(quantidade)
    except ValueError:
        return "Quantidade deve ser um número inteiro.", 400

    db, cursor = get_db()
    cursor.execute("SELECT id FROM pessoas WHERE usuario=?", [usuario])
    user_row = cursor.fetchone()
    if not user_row:
        db.close()
        return f"Usuário '{usuario}' não encontrado.", 404

    try:
        cursor.execute("UPDATE pessoas SET creditos = creditos + ? WHERE usuario=?", [quantidade_int, usuario])
        db.commit()
        db.close()
        return f"Sucesso! Injetados {quantidade_int} CR na conta de '{usuario}'."
    except Exception as e:
        print(e)
        if 'db' in locals():
            db.close()
        return "Erro interno ao processar injeção de créditos.", 500


@app.route("/logout")
def logout():
    db, cursor = get_db()
    db.close()
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
