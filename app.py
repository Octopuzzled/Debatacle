from app import create_app

# Claude suggested the separation of app.py and init
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)