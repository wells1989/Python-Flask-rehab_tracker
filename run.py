from app import app
import secrets

app.secret_key = secrets.token_hex(16) # needed for secure sessions

if __name__ == "__main__":
    app.run(debug=True) 