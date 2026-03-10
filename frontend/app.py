from flask import Flask, render_template, request, jsonify, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel, Field, EmailStr, ValidationError
from db.database import get_connection
from router.route import query_router
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Users(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return User(id=user[0], name=user[1], email=user[2])
    return None

@app.route("/", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        try:
            user = Users(
                name = request.form['name'],
                email = request.form['email'],
                password = request.form['password']
            )
            
        except ValidationError as e:
            errors = e.errors()
            return render_template(
                "signup.html",
                validation_error = errors,
                old_data = request.form
            )

        try:
            conn = get_connection()   # opens communication
            cur = conn.cursor()       # sends SQL

            cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            existing_user = cur.fetchone()

            if existing_user:
                cur.close()
                conn.close()
                return render_template(
                    "signup.html",
                    db_error="Email already registered",
                    old_data=request.form
                )

            hashed_password = generate_password_hash(user.password)

            cur.execute(              # runs query
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
                (user.name, user.email, hashed_password)
            )
            user_id = cur.fetchone()[0] 
            conn.commit()             # saves changes
            cur.close()               # cannot send sql
            conn.close()              # closes the connection

        except Exception as e:
            conn.rollback()
            return render_template(
                "signup.html",
                db_error = "Something went wrong",
                old_data = request.form
            )

        user_obj = User(id=user_id, name=user.name, email=user.email)
        login_user(user_obj)

        return render_template("dashboard.html", name=current_user.name)

    return render_template("signup.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return render_template(
                "login.html",
                validation_error="Email and password are required"
            )

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, password FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            conn.rollback()
            return render_template(
                "login.html",
                db_error = "Something went wrong"
            )
        
        if user is None:
            return render_template(
                "login.html",
                validation_error = "Invalid email or password"
            )
        
        user_id, name, stored_hash = user

        if check_password_hash(stored_hash, password):
            user_obj = User(id=user_id, name=name, email=email)
            login_user(user_obj)
            return render_template("dashboard.html", name=current_user.name)
        else:
            return render_template(
                "login.html",
                validation_error = "Invalid email or password"
            )
    
    return render_template("login.html")

@app.route('/ticker_search')
@login_required
def ticker_search():
    return render_template("ticker_search.html", name=current_user.name)

@app.route('/market_status')
@login_required
def market_status():
    return render_template("market_status.html", name=current_user.name)

@app.route('/new_chat')
@login_required
def new_chat():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessions (user_id) VALUES (%s) RETURNING id",
            (current_user.id,)
        )
        session_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return render_template(
            "new_chat.html",
            name=current_user.name,
            error="Session creation failed"
        )
    return redirect(f"/chat/{session_id}")

@app.route('/chat/<int:session_id>')
@login_required
def chat(session_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM sessions WHERE id = %s AND user_id = %s",
            (session_id, current_user.id)
        )
        valid_session = cur.fetchone()
        if not valid_session:
            return render_template("new_chat.html", name=current_user.name, error="Session loading failed")
        
        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = %s",
            (session_id,)
        )
        conversation = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return render_template("new_chat.html", name=current_user.name, error="Session loading failed")
    return render_template("new_chat.html", name=current_user.name, data = conversation, session_id=session_id)

@app.route('/api/search')
@login_required
def api_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol, name
        FROM tickers
        WHERE symbol ILIKE %s
        OR name ILIKE %s
        LIMIT 7
    """, (f"{query}%", f"{query}%"))

    results = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {"symbol": row[0], "name": row[1]}
        for row in results
    ])

@app.route('/query/<int:session_id>', methods=['POST'])
@login_required
def query(session_id):
    data = request.get_json()

    if not data or not data.get("q"):
        return jsonify({"session_id": session_id, "response": "No query provided"}), 403
    
    user_query = data["q"].strip()

    reply = query_router(user_query)

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, title FROM sessions WHERE id = %s AND user_id = %s",
            (session_id, current_user.id)
        )

        session = cur.fetchone()
        if not session:
            return jsonify({"session_id": session_id, "response": "Unauthorized"}), 403
        
        id, title = session

        if title is None:
            new_title = user_query[:10].strip()
            cur.execute("""
                UPDATE sessions
                SET title = %s
                WHERE id = %s
            """, (new_title, session_id))

        cur.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, "user", user_query)
        )
        cur.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, "assistant", reply)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"session_id": session_id, "response": "Conversation not saved"}), 500

    return jsonify({"session_id": session_id, "response": reply}) 

@app.context_processor
def inject_sidebar_sessions():
    if not current_user.is_authenticated:
        return dict(sessions=[])

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, title
            FROM sessions
            WHERE user_id = %s
            ORDER BY id DESC
        """, (current_user.id,))

        sessions = [{"id": row[0], "title": row[1]} for row in cur.fetchall()]

        cur.close()
        conn.close()

        return dict(sessions=sessions)

    except:
        return dict(sessions=[])

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)