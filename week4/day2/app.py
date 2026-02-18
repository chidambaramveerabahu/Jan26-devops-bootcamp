from flask import Flask, render_template_string, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'testdb')}"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

TEMPLATE = '''
<!DOCTYPE html>
<html><head><title>Simple App</title></head>
<body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
    <h1>User Registration</h1>
    <form method="POST">
        <input type="text" name="name" placeholder="Name" required style="padding: 8px; margin: 5px; width: 200px;"><br>
        <input type="email" name="email" placeholder="Email" required style="padding: 8px; margin: 5px; width: 200px;"><br>
        <button type="submit" style="padding: 10px 20px; margin: 5px;">Submit</button>
    </form>
    <h2>Users ({{ users|length }})</h2>
    <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <tr><th>ID</th><th>Name</th><th>Email</th></tr>
        {% for user in users %}
        <tr><td>{{ user.id }}</td><td>{{ user.name }}</td><td>{{ user.email }}</td></tr>
        {% endfor %}
    </table>
</body></html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = User(name=request.form['name'], email=request.form['email'])
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    users = User.query.all()
    return render_template_string(TEMPLATE, users=users)

# Create tables before first request
with app.app_context():
    db.create_all()
    print("✓ Database tables created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)