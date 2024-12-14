# File Upload App using Flask

---

**UPDATE 2024-12-14:** This is no longer a *work-in-progress*. This experiment is done. Keeping the notes below as-is. Archiving the repository for reference.

---

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
- [Fields / Convenience Fields](https://wtforms.readthedocs.io/en/3.0.x/fields/#convenience-fields)
- [Validators](https://wtforms.readthedocs.io/en/3.0.x/validators/)

---

[Flask-Login](https://flask-login.readthedocs.io/en/latest/) - Documentation

[Flask-Login](https://pypi.org/project/Flask-Login/) - PyPI

[maxcountryman/flask-login](https://github.com/maxcountryman/flask-login) - GitHub - Flask user session management.

---

Werkzeug Documentation:
- [generate_password_hash](https://werkzeug.palletsprojects.com/en/2.2.x/utils/#werkzeug.security.generate_password_hash)
- [check_password_hash](https://werkzeug.palletsprojects.com/en/2.2.x/utils/#werkzeug.security.check_password_hash)


---

 SQLAlchemy 1.4 Documentation: [Microsoft SQL Server](https://docs.sqlalchemy.org/en/14/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc)

[pyodbc](https://pypi.org/project/pyodbc/) - PyPI


[Install the Microsoft ODBC driver for SQL Server (Linux) - ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#ubuntu18) - Microsoft Learn


The first part of the instructions at the above Microsoft Learn link could be skipped because, in the host used for development, the Microsoft sources are already in `/etc/apt/sources.list.d/` from previously installing other MS tooling. Confirmed that by searching:

```bash
    apt-cache search msodbcsql
```

    msodbcsql17 - ODBC Driver for Microsoft(R) SQL Server(R)
    msodbcsql18 - ODBC Driver for Microsoft(R) SQL Server(R)

Installed the *ODBC Driver 18 for SQL Server* version:

```bash
    sudo apt install msodbcsql18
```
Note: The Linux containers used to host Azure Webapps have `msodbcsql18` installed.

---

[Quickstart: Deploy a Python (Django or Flask) web app to Azure](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cmac-linux%2Cazure-cli%2Czip-deploy%2Cdeploy-instructions-azcli%2Cterminal-bash%2Cdeploy-instructions-zip-azcli#3---deploy-your-application-code-to-azure) -  Microsoft Learn

[az webapp deploy](https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-deploy) - Microsoft Learn

---

[AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python) - GitHub
> Microsoft Authentication Library (MSAL) for Python makes it easy to authenticate to Azure Active Directory. These documented APIs are stable https://msal-python.readthedocs.io. If you have questions but do not have a github account, ask your questions on Stackoverflow with tag &quot;msal&quot; + &quot;python&quot;.

 Wiki: [AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki) - GitHub

[Microsoft identity platform overview](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-overview) - Microsoft Entra -  Microsoft Learn

[Flask-Session](https://pypi.org/project/Flask-Session/) - PyPI

[Quickstart: Sign in users in web apps using the auth code flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/web-app-quickstart?pivots=devlang-python) - Microsoft Entra - Microsoft Learn


## Notes

Using **Visual Studio Code** with the [cornflakes-linter](https://marketplace.visualstudio.com/items?itemName=kevinglasson.cornflakes-linter) and [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extensions.

Added settings to the `.vscode/settings.json` file for the project (not in repo). The `python.formatting.blackArgs` setting in this fragment overrides some of the [black](https://pypi.org/project/black/) formatter's defaults:

```json
"python.formatting.provider": "black",
"python.formatting.blackArgs": [
    "--skip-string-normalization",
    "--line-length",
    "79"
],
```

> I ended up removing the `--skip-string-normalization` setting. Even though I would prefer to use single quotes in most cases, because I have been using *black* in other projects, I am now in the habit of using double quotes, but not always. Therefore, I'll just let them be normalized for consistency. *-wem*

This fragment tells **Better Jinja** to treat HTML files as Jinja2 templates:

```json
"files.associations": {
    "*.html": "jinja-html"
}
```

---

Using `pip-compile`, part of [pip-tools](https://pypi.org/project/pip-tools/), to create/update `requirements.txt` from `requirements.in`.

GitHub: [jazzband/pip-tools](https://github.com/jazzband/pip-tools/): A set of tools to keep your pinned Python dependencies fresh.
