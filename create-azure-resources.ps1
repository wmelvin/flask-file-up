# ----------------------------------------------------------------------
# PowerShell script with steps to deploy using the Azure CLI.
#
# This script is intended to be executed in selected sections (F8 in IDE
# or paste into CLI), not all at once.
#
# ----------------------------------------------------------------------

# az login

# az account set -s $SUBSCRIPTION


$baseName = "fileup"


# -- Get key variables from file in local encrypted folder.

$keysFile = "$env:UserProfile\KeepLocal\${baseName}-settings.ps1"

# -- Source the file to set the vars.
. $keysFile

if (0 -eq $SqlAdminUser.Length) {
    Write-Host "Failed to get SqlAdminUser from '$keysFile'."
    Exit 1
}

if (0 -eq $SqlAdminPass.Length) {
  Write-Host "Failed to get SqlAdminPass from '$keysFile'."
  Exit 1
}


# -- Assign vars for script.
$rgName = "${baseName}-rg"
$location = "eastus"
$uniqtag = "31"
$appServiceName = "${baseName}${uniqtag}appserv"
$webAppName = "${baseName}${uniqtag}webapp"
# $appInsightsName = "${baseName}${uniqtag}insights"
$sqlServerName = "${baseName}${uniqtag}dbsrv"
$sqlDatabaseName = "${baseName}${uniqtag}sqldb"


# -- Create the Resource Group.
az group create -n $rgName -l $location


# SKIP
# # -- Create the Application Insights resource.
# #    https://docs.microsoft.com/en-us/cli/azure/resource?view=azure-cli-latest#az-resource-create

# az resource create -n $appInsightsName -g $rgName `
#   --resource-type "Microsoft.Insights/components" `
#   --properties '{\"Application_Type\":\"web\"}'


# -- Create the App Service Plan (Linux).
#    https://docs.microsoft.com/en-us/cli/azure/appservice/plan?view=azure-cli-latest#az-appservice-plan-create

az appservice plan create `
  --name $appServiceName `
  --resource-group $rgName `
  --is-linux `
  --sku s1



# -- Create the Web App.
#    https://docs.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-create
#
#    az webapp list-runtimes

az webapp create `
  -g $rgName `
  -p $appServiceName `
  --name $webAppName `
  --runtime "PYTHON:3.10"


# -- Create SQL Server.
#    https://docs.microsoft.com/en-us/cli/azure/sql/server?view=azure-cli-latest#az-sql-server-create

az sql server create --name $sqlServerName -g $rgName `
  --location $location `
  --admin-password $SqlAdminPass `
  --admin-user $SqlAdminUser


# -- Add firewall rules for the web app's outbound IP addresses to the SQL Server.
#    https://docs.microsoft.com/en-us/azure/app-service/overview-inbound-outbound-ips#find-outbound-ips
#    https://docs.microsoft.com/en-us/cli/azure/sql/server/firewall-rule?view=azure-cli-latest#az-sql-server-firewall-rule-create

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

az sql db create --name $sqlDatabaseName -g $rgName --server $sqlServerName



# -- Get the connection string.
# $connStr = $(az sql db show-connection-string -s $sqlServerName -n $sqlDatabaseName -c ado.net)


# -- To add the local IP to the Database Server in the Azure Portal:
#    - Select the Resource Group.
#    - Select the SQL Server.
#    - Select the Networking blade.
#    - Scroll to Firewall Rules.
#    - Select 'Add your client IPv4 address'.
#    - Click 'Save'.


# -- List resources.
# az resource list -g $rgName -o table


# -- Delete the whole lot when done.
# az group delete -n $rgName
