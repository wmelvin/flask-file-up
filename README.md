# File Upload App using Flask

> This is a work-in-progress demo. If it works out, a LICENSE will be added when it is done. Otherwise this repository will probably go away.

<sub>Created: 2022-10-18</sub>

## Links

[Flask Documentation](https://flask.palletsprojects.com/en/latest/)

[Modular Applications with Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/)

Use [flask.current_app](https://flask.palletsprojects.com/en/latest/api/#flask.current_app) to access `app.config` values in view modules using blueprints. Only available in the [Request Context](https://flask.palletsprojects.com/en/latest/reqcontext/#notes-on-proxies).

---

[SQLAlchemy](https://www.sqlalchemy.org/)
- [Column](https://docs.sqlalchemy.org/en/14/core/metadata.html?highlight=column#sqlalchemy.schema.Column)
- [Column INSERT/UPDATE Defaults](https://docs.sqlalchemy.org/en/14/core/defaults.html)
- [The Type Hierarchy](https://docs.sqlalchemy.org/en/14/core/type_basics.html#the-camelcase-datatypes)

---

[flask-sqlalchemy](https://pypi.org/project/flask-sqlalchemy/) - PyPI

[Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)

[flask-sqlalchemy](https://github.com/pallets-eco/flask-sqlalchemy/) - GitHub


[Flask-Migrate](https://pypi.org/project/Flask-Migrate/) - PyPI

[miguelgrinberg/Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate) - GitHub - SQLAlchemy database migrations for Flask applications using Alembic.

[alembic](https://pypi.org/project/alembic/) - PyPI

[Alembic documentation](https://alembic.sqlalchemy.org/en/latest/)

---

[Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/) - Documentation

[Flask-WTF](https://pypi.org/project/Flask-WTF/) - PyPI

[WTForms](https://wtforms.readthedocs.io/en/3.0.x/) - Documentation

---

[Flask-Login](https://flask-login.readthedocs.io/en/latest/) - Documentation

[Flask-Login](https://pypi.org/project/Flask-Login/) - PyPI

[maxcountryman/flask-login](https://github.com/maxcountryman/flask-login) - GitHub - Flask user session management.


## Notes

Using **Visual Studio Code** with the [cornflakes-linter](https://marketplace.visualstudio.com/items?itemName=kevinglasson.cornflakes-linter) and [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extensions.

Added settings to the `.vscode/settings.json` file for the project (not in repo).

The `python.formatting.blackArgs` setting in this fragment overrides some of the **black** formatter's defaults:

```json
"python.formatting.provider": "black",
"python.formatting.blackArgs": [
    "--skip-string-normalization",
    "--line-length",
    "79"
],
```

This fragment tells **Better Jinja** to treat HTML files as Jinja2 templates:

```json
"files.associations": {
    "*.html": "jinja-html"
}
```

---

Using `pip-compile`, part of [pip-tools](https://pypi.org/project/pip-tools/), to create/update `requirements.txt` from `requirements.in`.

GitHub: [jazzband/pip-tools](https://github.com/jazzband/pip-tools/): A set of tools to keep your pinned Python dependencies fresh.
