# ======================================================================
#  PowerShell script with steps to deploy using the Azure CLI.
#
#  Some commented-out commands in this script are intended to be executed
#  separately using F8 in an IDE (or by pasting into a shell to run).
#
#  Running this script will:
#  - Create a Resource Group.
#  - Create an App Service Plan (Linux).
#  - Create a Web App.
#  - Configure the Web App for ZIP file deployment.
#  - Create SQL Server.
#  - Add firewall rules to the SQL Server.
#  - Create a Database on the SQL Server.
#
# ----------------------------------------------------------------------

# az login

# az account set -s $SUBSCRIPTION

# ----------------------------------------------------------------------
# Script initialization:

$baseName = "fileup"

# -- Get key variables from file in local encrypted folder.

$keysFile = "$env:UserProfile\KeepLocal\${baseName}-settings.ps1"

# -- The file must set these variables:
#  $sqlAdminUser = ""
#  $sqlAdminPass = ""
#  $appSecretKey = ""
#  $appMaxUploadSizeMb = ""

# -- Source the file to set the vars.
. $keysFile

# -- Check that the required variables were set.
function CheckVarSet ([string] $varName) {
    $val = Get-Variable -Name $varName -ValueOnly -ErrorAction:Ignore
    if (0 -eq $val.Length) {
      Write-Host "ERROR: '$varName' not set in '$keysFile'."
      Exit 1
    }
}

CheckVarSet "sqlAdminUser"
CheckVarSet "sqlAdminPass"
CheckVarSet "appSecretKey"
CheckVarSet "appMaxUploadSizeMb"


# -- Assign additional variables used in this script.

$rgName = "${baseName}-rg"
$location = "eastus"
$uniqtag = "31"
$appServiceName = "${baseName}${uniqtag}appserv"
$webAppName = "${baseName}${uniqtag}webapp"
# $appInsightsName = "${baseName}${uniqtag}insights"
$sqlServerName = "${baseName}${uniqtag}dbsrv"
$sqlDatabaseName = "${baseName}${uniqtag}sqldb"

$escpw = [uri]::EscapeDataString($SqlAdminPass)
$appDatabaseURI = "mssql+pyodbc://${sqlAdminUser}:${escpw}@${sqlServerName}.database.windows.net:1433/${sqlDatabaseName}?driver=ODBC+Driver+18+for+SQL+Server"


# ======================================================================
# Create and configure Azure resources.

Write-Host "`nSTEP - Creating resource group: $rgName`n"

az group create -n $rgName -l $location


# SKIP
# # -- Create the Application Insights resource.
# #    https://docs.microsoft.com/en-us/cli/azure/resource?view=azure-cli-latest#az-resource-create

# az resource create -n $appInsightsName -g $rgName `
#   --resource-type "Microsoft.Insights/components" `
#   --properties '{\"Application_Type\":\"web\"}'


# -- Create the App Service Plan (Linux).
#    https://docs.microsoft.com/en-us/cli/azure/appservice/plan?view=azure-cli-latest#az-appservice-plan-create

Write-Host "`nSTEP - Creating App Service Plan: $appServiceName`n"

az appservice plan create `
  --name $appServiceName `
  --resource-group $rgName `
  --is-linux `
  --sku s1



# -- Create the Web App.
#    https://docs.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-create
#
#    az webapp list-runtimes

Write-Host "`nSTEP - Creating Web App: $webAppName`n"

az webapp create `
  -g $rgName `
  -p $appServiceName `
  --name $webAppName `
  --runtime "PYTHON:3.10"


# -- Configure for ZIP file deployment.
#    https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Czip-deploy%2Cdeploy-instructions-azcli%2Cterminal-bash%2Cdeploy-instructions-zip-azcli#3---deploy-your-application-code-to-azure

Write-Host "`nSTEP - Configuring settings for: $webAppName`n"

az webapp config appsettings set `
    -g $rgName `
    --name $webAppName `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true


# -- Configure settings for the web app. These are available to the app as environment variables.

Write-Host "`nSTEP - Configuring web app settings for: $webAppName`n"

az webapp config appsettings set `
    -g $rgName `
    --name $webAppName `
    --settings "FILEUP_SECRET_KEY=$AppSecretKey" `
    "FILEUP_MAX_UPLOAD_MB=$AppMaxUploadSizeMb" `
    "FILEUP_DATABASE_URI=$AppDatabaseURI"


# -- Create SQL Server.
#    https://docs.microsoft.com/en-us/cli/azure/sql/server?view=azure-cli-latest#az-sql-server-create

Write-Host "`nSTEP - Creating SQL Server: $sqlServerName`n"

az sql server create --name $sqlServerName -g $rgName `
  --location $location `
  --admin-password $SqlAdminPass `
  --admin-user $SqlAdminUser


# -- Add firewall rules for the web app's outbound IP addresses to the SQL Server.
#    https://docs.microsoft.com/en-us/azure/app-service/overview-inbound-outbound-ips#find-outbound-ips
#    https://docs.microsoft.com/en-us/cli/azure/sql/server/firewall-rule?view=azure-cli-latest#az-sql-server-firewall-rule-create

Write-Host "`nSTEP - Adding firewall rules for: $sqlServerName`n"

$ipAddresses = az webapp show -g $rgName --name $webAppName --query outboundIpAddresses --output tsv
$ipNum = 0
foreach ($ip in $ipAddresses.Split(","))
{
  $ipNum += 1
  $ruleName = "WebAppIP$ipNum"
  Write-Host $ruleName $ip
  az sql server firewall-rule create -g $rgName -s $sqlServerName -n $ruleName --start-ip-address $ip --end-ip-address $ip
}



# -- Create SQL Database.
#    https://docs.microsoft.com/en-us/cli/azure/sql/db?view=azure-cli-latest#az-sql-db-create

Write-Host "`nSTEP - Creating database: $sqlDatabaseName`n"

az sql db create --name $sqlDatabaseName -g $rgName --server $sqlServerName



# -- Set custom startup command for running the Flask app.
#    https://learn.microsoft.com/en-us/azure/app-service/configure-language-python#customize-startup-command

Write-Host "`nSTEP - Configure startup command for: $webAppName`n"

$startCmd = "gunicorn --bind=0.0.0.0 --timeout 600 --chdir fileup_app fileup:app"
az webapp config set -g $rgName --name $webAppName --startup-file $startCmd



# ----------------------------------------------------------------------
# Additional commands and information.


# -- Zip deploy (update $zipFile value before running).
#    https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-deploy
#
# $zipFile = "../deploy/fileup_20221102_01.zip"
# az webapp deploy --name $webAppName -g $rgName --src-path $zipFile


# -- To add the local IP to the Database Server in the Azure Portal:
#    - Select the Resource Group.
#    - Select the SQL Server.
#    - Select the Networking blade.
#    - Scroll to Firewall Rules.
#    - Select 'Add your client IPv4 address'.
#    - Click 'Save'.


# -- Get the database connection string. The Flask app does not use this.
#
# $connStr = $(az sql db show-connection-string -s $sqlServerName -n $sqlDatabaseName -c ado.net)


# -- List resources.
#
# az resource list -g $rgName -o table


# -- Delete the whole lot when done.
#
# az group delete -n $rgName
