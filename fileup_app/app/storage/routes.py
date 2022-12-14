import os
import tempfile
from pathlib import Path

from app import db
from app.models import Org, Purpose, UploadedFile, User
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    url_for,
)
from rich import print as rprint
from werkzeug.datastructures import FileStorage

# from azure.core.exceptions import ResourceExistsError


bp = Blueprint("storage", __name__, template_folder="templates")


def store_uploaded_file(
    file_name: str,
    org: Org,
    user: User,
    purpose: Purpose,
    file_data: FileStorage,
):
    """
    If Azure Storage is configured, the uploaded file will be stored
    in a blob container. Otherwise the uploaded file is written to
    the UPLOAD_PATH on the host.

    After the file is stored, a UploadedFile record is inserted in
    the database.
    """

    if (
        current_app.config["STORAGE_ACCOUNT_URL"]
        or current_app.config["STORAGE_CONNECTION"]
    ):
        storage_name = (
            f"AzureContainer:{current_app.config['STORAGE_CONTAINER']}"
        )
        # TODO: Perhaps storage_name should hold the blob URL for the uploaded
        #  file, depenging on what any downstream processing needs. The column
        #  type might need to be larger than the current String(255).

        _saveToBlob(file_name, file_data)
    else:
        upload_path = current_app.config["UPLOAD_PATH"]
        storage_name = f"FileSystem:{upload_path}"
        file_data.save(os.path.join(upload_path, file_name))

    uf: UploadedFile = UploadedFile(
        file_name,
        org.id,
        org.org_name,
        user.id,
        user.username,
        purpose.id,
        purpose.tag,
        storage_name,
    )
    db.session.add(uf)
    db.session.commit()


def _saveToBlob(file_name: str, file_data: FileStorage):
    try:
        #  Prefer using the DefaultAzureCredential if configured.
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

        container_name = current_app.config["STORAGE_CONTAINER"]

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
