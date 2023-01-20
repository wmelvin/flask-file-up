### 2022-11-02

Ran the `az-setup.ps1` script to create and configure Azure resources.

In the Azure portal, added the client IP address to the firewall rules.

---

**To add the local client IP address to the Database Server in the Azure Portal:**
- Select the **Resource Group**.
- Select the **SQL Server**.
- Select the **Networking** blade.
- Scroll to **Firewall Rules**.
- Select the **Add your client IPv4 address** link.
- Click **Save**.

---

**Prepare the Azure SQL database**

In the project, loaded in VS-Code, on the local dev machine.

Set `FILEUP_DATABASE_URI` in `.env` to the `mssql+pyodbc://...` connection string as currently configured in Azure.

In the terminal:

Activate the virtual environment and change to the home directory for the app.
    
    . venv/bin/activate
    
    cd fileup_app

Apply the database migrations to create tables in the Azure SQL database.
    
    flask db upgrade
    
Open the Flask shell (a Python shell that has the Flask app context).

    flask shell
    
In the Python shell, run the `seed_db()` function to seed the database. This function gets data from local CSV files located outside the project path.

    >>> seed_db()
    
Press `Ctrl`+`D` to exit the shell.

The above steps used the Flask app running locally to modify the Azure SQL database, but the Flask app itself is not yet in Azure.

**Create a project ZIP file to deploy**

Created a ZIP file containing the Flask app, with some items excluded. This may be automated later, but for now it is a manual process.

Used the diff-tool, Beyond Compare (bcompare), to sync the project files to a separate folder (`~/pkg`), filtering out some files and folders that should not be deployed.

```bash
bcompare ${src} ~/pkg/fileup \
  -filters="-.env;-*.ps1;-*.sqlite;-.*/;-__pycache__//;-venv//;-uploads//"
```

The `zip` command is run manually to create the file to be deployed.

```bash
cd ~/pkg/fileup
zip -r fileup_20221102_01.zip .
```

**Deploy the ZIP file to Azure**

In PowerShell terminal (`$webAppName` and `$rgName` were already set from running `az-setup.ps1`):

```powershell
    $zipFile = "${PATH_TO_DEPLOY}/fileup_20221102_01.zip"
    
    az webapp deploy --name $webAppName -g $rgName --src-path $zipFile
```

Opened the web app in the browser at `https://fileup31.webapp.azurewebsites.net`. The `31` in the app name is a unique-tag used in creating the Azure resources. 

Successfully signed in using the credentials seeded in the database.

Successfully uploaded a file. At this point uploads are still going to a local 'uploads' folder on the web host.

---

### 2022-11-22

Repeated the above deployment steps. The `az-setup.ps1` script has been updated to include multiple new configuration settings since the previous deployment test.

This time, the `FILEUP_STORAGE_CONNECTION` and `FILEUP_STORAGE_CONTAINER` settings were used to connect to an Azure Storage Blob container for a deployed instance of another demo application called [FunciSox](https://github.com/wmelvin/funcisox).

That *Azure Durable Functions* application includes a blob-triggered function. It was successfully triggered by using **fileup_app**, also running on Azure, to upload a *.mp3* file to the container.

---
