from app import create_app, db

from seed_db import seed_db


app = create_app()

# with app.app_context():
#     seed_db()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "seed_db": seed_db}
