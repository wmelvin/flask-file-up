import tempfile

from pathlib import Path

from rich import print as rprint

from flask import Blueprint, current_app, flash, redirect, url_for

from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient

# from azure.core.exceptions import ResourceExistsError

from app.auth.routes import current_user, login_required


bp = Blueprint("storage", __name__, template_folder="templates")


@bp.route("/checkstorage", methods=["GET"])
def check_storage():
    try:
        conn_str = current_app.config["STORAGE_CONNECTION"]
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


@bp.route("/upload2", methods=["POST"])
@login_required
def upload_to_storage():
    print(current_user)
    flash("Not implemented.")
    return redirect(url_for("main.index"))
    # TODO: ...
