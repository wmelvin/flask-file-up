from rich.traceback import install
install(show_locals=True)

from app import create_app, db  # noqa E402

from seed_db import seed_db  # noqa E402


app = create_app()

# print(f"*** {app.debug=}")

# with app.app_context():
#     seed_db()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "seed_db": seed_db}
