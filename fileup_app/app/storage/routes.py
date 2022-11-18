import os
import tempfile
from pathlib import Path

from app import db
from app.auth.routes import current_user, login_required
from app.main.forms import UploadForm
from app.models import Org, Purpose, UploadedFile, User
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from rich import print as rprint
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# from azure.core.exceptions import ResourceExistsError


bp = Blueprint("storage", __name__, template_folder="templates")


def saveToBlob(file_name: str, file_data: FileStorage):
    try:
        acct_url = current_app.config["STORAGE_ACCOUNT_URL"]
        if acct_url:
            default_cred = DefaultAzureCredential()
            service_client: BlobServiceClient = BlobServiceClient(
                acct_url, credential=default_cred
            )
        else:
            conn_str = current_app.config["STORAGE_CONNECTION"]
            if not conn_str:
                flash("Upload failed: Missing storage configuration.")
                return redirect(url_for("main.index"))

            service_client: BlobServiceClient = (
                BlobServiceClient.from_connection_string(conn_str)
            )

        container_name = "fileup"
        # TODO: Config this.

        container_client: ContainerClient = (
            service_client.get_container_client(container_name)
        )
        if container_client.exists():
            rprint(f"Container exists: '{container_client.container_name}'")
        else:
            container_client: ContainerClient = (
                service_client.create_container(container_name)
            )
            rprint(f"Created container: '{container_client.container_name}'")

        blob_client: BlobClient = container_client.get_blob_client(
            blob=file_name
        )

        if blob_client.exists():
            rprint(f"Blob exists: '{blob_client.blob_name}'")
        else:
            blob_client.upload_blob(file_data)

    except Exception as ex:
        rprint("Exception:")
        rprint(ex)
        flash("Upload failed.")
        return redirect(url_for("main.index"))


@bp.route("/checkstorage", methods=["GET"])
def check_storage():
    if "CheckStorage" not in current_app.config["ENABLE_FEATURES"]:
        return redirect(url_for("main.index"))

    try:
        acct_url = current_app.config["STORAGE_ACCOUNT_URL"]
        if acct_url:
            default_cred = DefaultAzureCredential()
            service_client: BlobServiceClient = BlobServiceClient(
                acct_url, credential=default_cred
            )
        else:
            conn_str = current_app.config["STORAGE_CONNECTION"]
            if not conn_str:
                flash("check_storage: Not configured to access storage.")
                return redirect(url_for("main.index"))

            service_client: BlobServiceClient = (
                BlobServiceClient.from_connection_string(conn_str)
            )

        container_name = "fileup"

        container_client: ContainerClient = (
            service_client.get_container_client(container_name)
        )
        if container_client.exists():
            rprint(f"Container exists: '{container_client.container_name}'")
        else:
            container_client: ContainerClient = (
                service_client.create_container(container_name)
            )
            rprint(f"Created container: '{container_client.container_name}'")

        test_file = Path(tempfile.gettempdir()) / "fileup-test.txt"

        blob_client: BlobClient = container_client.get_blob_client(
            blob=test_file.name
        )

        if blob_client.exists():
            rprint(f"Blob exists: '{blob_client.blob_name}'")
        else:
            test_file.write_text("Testing...")
            with open(test_file, "rb") as f:
                blob_client.upload_blob(f)

    except Exception as ex:
        rprint("Exception:")
        rprint(ex)
        flash("check_storage: failed")
        return redirect(url_for("main.index"))

    flash("check_storage: success")
    return redirect(url_for("main.index"))


@bp.route("/upload2")
@login_required
def upload2():
    # Get list of tuples to use in radio button input.
    purposes = [(p.title, p.title) for p in Purpose.query.all()]

    files = current_user.get_uploaded_file_list()

    #  Get list of accepted file extensions.
    ext_list = current_app.config["UPLOAD_EXTENSIONS"]
    if ext_list:
        accept = ",".join(ext_list)
    else:
        print("No UPLOAD_EXTENSIONS configured. Default to '.csv'.")
        accept = ".csv"

    form = UploadForm()
    form.purpose.choices = purposes

    return render_template(
        "upload.html", form=form, files=files, accept=accept
    )


@bp.route("/upload2", methods=["POST"])
@login_required
def upload_files2():
    upload_url = "storage.upload2"
    up_files = request.files.getlist("file")
    if (not up_files) or (len(up_files[0].filename) == 0):
        flash("No file(s) selected.")
        return redirect(url_for(upload_url))

    user: User = current_user
    org: Org = Org.query.get(user.org_id)

    if "purpose" in request.form:
        purpose_input = request.form["purpose"]
    else:
        purpose_input = ""
    if not purpose_input:
        flash("A 'Purpose of File' selection is required.")
        return redirect(url_for(upload_url))

    purpose: Purpose = Purpose.query.filter_by(title=purpose_input).first()

    print(f"upload_files: user='{user}', org='{org}', purpose='{purpose}'")

    for up_file in up_files:
        #  up_file is type 'werkzeug.datastructures.FileStorage'
        file_name = secure_filename(up_file.filename)
        if file_name != "":
            file_ext = os.path.splitext(file_name)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
                flash(f"Invalid file type: '{file_ext}'")
                return redirect(url_for(upload_url))

            file_name = f"fileup-u{user.id}-{purpose.get_tag()}-{file_name}"

            # up_file.save(
            #     os.path.join(current_app.config["UPLOAD_PATH"], file_name)
            # )

            saveToBlob(file_name, up_file)

            uf: UploadedFile = UploadedFile(
                file_name,
                org.id,
                org.org_name,
                user.id,
                user.username,
                purpose.id,
                purpose.tag,
            )
            db.session.add(uf)
            db.session.commit()

    return redirect(url_for(upload_url))
