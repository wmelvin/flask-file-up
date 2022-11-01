import csv

from pathlib import Path

from app import db
from app.models import Purpose, Org, User


def seed_purposes(data_path: Path):
    if Purpose.query.count():
        print("Purpose table already has data.")
    else:
        csv_file = data_path / "seed_purposes.csv"
        if not (csv_file.exists() and csv_file.is_file()):
            print(f"seed_purposes: Cannot find '{csv_file}'.")
            return
        print(f"Reading '{csv_file}'.")
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            assert "title" in reader.fieldnames
            for row in reader:
                p: Purpose = Purpose()
                p.title = row["title"]
                p.tag = row["tag"]
                p.description = row["description"]
                if p.title and p.tag:
                    db.session.add(p)
                    db.session.commit()


def seed_orgs(data_path: Path):
    if Org.query.count():
        print("Org table already has data.")
    else:
        csv_file = data_path / "seed_orgs.csv"
        if not (csv_file.exists() and csv_file.is_file()):
            print(f"seed_orgs: Cannot find '{csv_file}'.")
            return
        print(f"Reading '{csv_file}'.")
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            assert "org_name" in reader.fieldnames
            for row in reader:
                o: Org = Org()
                o.org_name = row["org_name"]
                if o.org_name:
                    db.session.add(o)
                    db.session.commit()


def seed_users(data_path: Path):
    if User.query.count():
        print("User table already has data.")
    else:
        csv_file = data_path / "seed_users.csv"
        if not (csv_file.exists() and csv_file.is_file()):
            print(f"seed_users: Cannot find '{csv_file}'.")
            return
        print(f"Reading '{csv_file}'.")
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            assert "username" in reader.fieldnames
            for row in reader:
                org_name = row["org_name"]
                if not org_name:
                    continue
                org = Org.query.filter_by(org_name=org_name).first()
                if not org:
                    continue
                u: User = User()
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

    seed_purposes(seed_data_path)
    seed_orgs(seed_data_path)
    seed_users(seed_data_path)
