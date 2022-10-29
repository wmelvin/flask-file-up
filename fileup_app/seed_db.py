import csv

from pathlib import Path

from app import db
from app.models import Org, User


def seed_orgs(data_path: Path):
    if Org.query.count():
        print("Org table already has data.")
    else:
        orgs_file = data_path / "seed_orgs.csv"
        if not (orgs_file.exists() and orgs_file.is_file()):
            print(f"seed_orgs: Cannot find '{orgs_file}'.")
            return
        print(f"Reading '{orgs_file}'.")
        with open(orgs_file) as f:
            orgs_reader = csv.DictReader(f)
            assert "org_name" in orgs_reader.fieldnames
            for row in orgs_reader:
                o = Org()
                o.org_name = row["org_name"]
                if o.org_name:
                    db.session.add(o)
                    db.session.commit()


def seed_users(data_path: Path):
    if User.query.count():
        print("User table already has data.")
    else:
        users_file = data_path / "seed_users.csv"
        if not (users_file.exists() and users_file.is_file()):
            print(f"seed_users: Cannot find '{users_file}'.")
            return
        print(f"Reading '{users_file}'.")
        with open(users_file) as f:
            users_reader = csv.DictReader(f)
            assert "username" in users_reader.fieldnames
            for row in users_reader:
                org_name = row["org_name"]
                if not org_name:
                    continue
                org = Org.query.filter_by(org_name=org_name).first()
                if not org:
                    continue
                u = User()
                u.org_id = org.id
                u.username = str(row["username"])
                u.email = str(row["email"])
                u.active = True
                u.set_password(str(row["password"]))
                db.session.add(u)
                db.session.commit()


def seed_db():
    seed_data_path = Path("~/KeepLocal/fileup").expanduser().resolve()
    # TODO: Put seed data path in env var?

    if not (seed_data_path.exists() and seed_data_path.is_dir()):
        print(f"seed_db: Cannot find data path '{seed_data_path}'.")
        return

    seed_orgs(seed_data_path)
    seed_users(seed_data_path)
