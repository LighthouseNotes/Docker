import yaml
from getpass import getpass
import random
import secrets
import shutil

# Function to generate a shuffled alphabet=
def shuffled_alphabet():
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    random.shuffle(alphabet)
    return ''.join(alphabet)

# ANSI escape codes for colors
COLOR_BLUE   = "\033[94m"  
COLOR_YELLOW = "\033[93m" 
COLOR_GREEN  = "\033[92m"  
COLOR_END    = "\033[0m"   

###########
# Welcome #
###########
print(f"\n{COLOR_GREEN}Starting Lighthouse Notes configuration generator...{COLOR_END}\n") 

########
# Load #
#########
# Load sample-docker-compose.yml
with open('docker-compose.sample.yml', 'r') as yaml_file:
    compose = yaml.safe_load(yaml_file)

###############################
# Fix YML for JSON conversion #
###############################
# Loop through each service
for service, service_config in compose['services'].items():
    # Extract environment variables
    environment_vars = service_config.get('environment', [])

    # Convert environment variables to a list of dictionaries
    environment = {}
    for var in environment_vars:
        if '=' in var:
            key, value = var.split('=', 1)  # Split only at the first occurrence of '=' to support values containing '='
            environment[key] = value
        else:
            environment[key] = ""

    if environment:
        # Add the list of dictionaries to the service configuration
        service_config['environment'] = environment

###############
# User inputs #
###############
print("\nPlease enter the requested data at each prompt and press enter.\n")

root_domain = input(f"Root domain (e.g., {COLOR_BLUE}example.com{COLOR_END}): ")

auth0_domain = input(f"Auth0 Domain (e.g., {COLOR_BLUE}example.auth0.com{COLOR_END}): ")
auth0_audience = input(f"Auth0 Audience (e.g., {COLOR_BLUE}https://api.example.com{COLOR_END}): ")

syncfusion_license_key = input (f"Syncfusion License Key {COLOR_YELLOW}(Get from: https://www.syncfusion.com/account/downloads){COLOR_END}: ")

certificate_password = getpass(f"Certificate Password {COLOR_GREEN}(input will not show){COLOR_END}: ")

database_password = secrets.token_urlsafe(14)

##########
# Server #
##########
# Auth0
compose["services"]["server"]["environment"]["Auth0__DOMAIN"] = auth0_domain
compose["services"]["server"]["environment"]["Auth0__Audience"] = auth0_audience

# Connection string
compose["services"]["server"]["environment"]["ConnectionStrings__Database"] = f"Host=database;Database=lighthousenotes;Username=lighthousenotes;Password={database_password}"

# Sqids
compose["services"]["server"]["environment"]["Sqids__Alphabet"] = shuffled_alphabet() 

# Syncfusion
compose["services"]["server"]["environment"]["Syncfusion__LicenseKey"] = syncfusion_license_key

# Web app
compose["services"]["server"]["environment"]["WebApp"] = f"https://app.{root_domain}" 

#######
# Web #
#######
# Certificate
compose["services"]["web"]["environment"]["Certificates__Default__Password"] = certificate_password

# Auth0
compose["services"]["web"]["environment"]["Auth0__DOMAIN"] = auth0_domain

# Auth0 Authentication
compose["services"]["web"]["environment"]["Auth0__Auth__Audience"] = auth0_audience
compose["services"]["web"]["environment"]["Auth0__Auth__ClientId"] = input(f"Authentication client ID  {COLOR_YELLOW}(Dashboard > Applications > Applications > Lighthouse Notes){COLOR_END}: ")
compose["services"]["web"]["environment"]["Auth0__Auth__ClientSecret"] = input(f"Authentication client secret {COLOR_YELLOW}(Dashboard > Applications > Applications > Lighthouse Notes){COLOR_END}: ")

# Auth0 Management
compose["services"]["web"]["environment"]["Auth0__Management__Audience"] = auth0_audience
compose["services"]["web"]["environment"]["Auth0__Management__ClientId"] = input(f"Management client ID {COLOR_YELLOW}(Dashboard > Applications > Applications > Lighthouse Notes M2M){COLOR_END}: ")
compose["services"]["web"]["environment"]["Auth0__Management__ClientSecret"] =  input(f"Management client secret {COLOR_YELLOW}(Dashboard > Applications > Applications > Lighthouse Notes M2M){COLOR_END}: ")

# Auth0 Role IDs
compose["services"]["web"]["environment"]["Auth0__Roles__user"] = input(f"User role ID {COLOR_YELLOW}(Dashboard > User Management > Roles > user){COLOR_END}: ")
compose["services"]["web"]["environment"]["Auth0__Roles__sio"] = input(f"SIO role ID {COLOR_YELLOW}(Dashboard > User Management > Roles > sio){COLOR_END}: ")
compose["services"]["web"]["environment"]["Auth0__Roles__organization-administrator"] = input(f"Organization-administrator role ID {COLOR_YELLOW}(Dashboard > User Management > Roles > organization-administrator){COLOR_END}: ")

# Auth0 Connection ID
compose["services"]["web"]["environment"]["Auth0__ConnectionId"] = input(f"Connection ID {COLOR_YELLOW}(Dashboard > Authentication > Database > Username-Password-Authentication){COLOR_END}: ")

# Syncfusion
compose["services"]["web"]["environment"]["Syncfusion__LicenseKey"] = syncfusion_license_key

# API Url
compose["services"]["web"]["environment"]["LighthouseNotesApiUrl"] = f"https://api.{root_domain}"

########
# SWAG #
########
compose["services"]["swag"]["environment"]["URL"] = root_domain

############
# Postgres #
############
compose["services"]["database"]["environment"]["POSTGRES_PASSWORD"] = database_password
compose["services"]["database"]["environment"]["POSTGRES_ROOT_PASSWORD"] = secrets.token_urlsafe(14)

#########
# Minio #
#########
# Certificate volumes
compose["services"]["minio"]["volumes"][1] = f"./swag/etc/letsencrypt/live/app.{root_domain}/fullchain.pem:/root/.minio/certs/public.crt"
compose["services"]["minio"]["volumes"][2] = f"./swag/etc/letsencrypt/live/app.{root_domain}/privkey.pem:/root/.minio/certs/private.key"
compose["services"]["minio"]["volumes"][3] = f"./swag/etc/letsencrypt/live/app.{root_domain}/fullchain.pem:/root/.minio/certs/CAs/public.crt"
compose["services"]["minio"]["volumes"][4] = f"./swag/etc/letsencrypt/live/app.{root_domain}/privkey.pem:/root/.minio/certs/CAs/private.key"


compose["services"]["minio"]["environment"]["MINIO_SERVER_URL"] = f"https://s3.{root_domain}"
compose["services"]["minio"]["environment"]["MINIO_ROOT_PASSWORD"] = getpass(f"Minio root password {COLOR_GREEN}(input will not show){COLOR_END}: ")

###############
# Meilisearch #
###############
meilisearch_master_key = secrets.token_urlsafe(42)  
compose["services"]["meilisearch"]["environment"]["MEILI_MASTER_KEY"] = meilisearch_master_key

###############################
# Fix JSON for YML conversion #
###############################
# Loop through each service
for service, service_config in compose['services'].items():

    if "environment" in service_config:
        # Extract environment variables
        environment_vars = service_config["environment"]

        # Convert environment variables to a list of dictionaries
        environment = []
        for key, value in environment_vars.items():
            environment.append(f"{key}={value}")

        if environment:
            # Add the list of dictionaries to the service configuration
            service_config['environment'] = environment

# Save the modified yml to file
with open('docker-compose.yml', 'w') as final_compose:
    yaml.dump(compose, final_compose, default_flow_style=False, sort_keys=False)

#######################
# Nginx configuration #
########################
shutil.move(f'site-confs/api.example.com.conf', f'site-confs/api.{root_domain}.conf')
with open(f'site-confs/api.{root_domain}.conf', 'r+') as api_site_config:
    data = api_site_config.read()
    api_site_config.seek(0)
    data = data.replace('example.com', root_domain)
    api_site_config.write(data)
    api_site_config.truncate()


shutil.move(f'site-confs/app.example.com.conf', f'site-confs/app.{root_domain}.conf')
with open(f'site-confs/app.{root_domain}.conf', 'r+') as app_site_config:
    data = app_site_config.read()
    app_site_config.seek(0)
    data = data.replace('example.com', root_domain)
    app_site_config.write(data)
    app_site_config.truncate()


#######
# SQL #
#######
print("\nPlease enter the requested data at each prompt and press enter.")
print("This information will be used to generate the SQL file which seeds the database.\n")
# Organization
organization_id = input(f"Organization ID {COLOR_YELLOW}(Dashboard > Organizations){COLOR_END}: ")
organization_name = input(f"Organization Name {COLOR_YELLOW}(Dashboard > Organizations){COLOR_END}: ")
organization_display_name = input(f"Organization Display Name {COLOR_YELLOW}(Dashboard > Organizations){COLOR_END}: ")

organization_sql = f"INSERT INTO \"Organization\" (\"Id\", \"Name\", \"DisplayName\", \"Created\", \"Modified\") VALUES ('{organization_id}', '{organization_name}', '{organization_display_name}', NOW(), NOW());"

# User
user_id = input(f"User ID {COLOR_YELLOW}(Dashboard > User Management > Your Name){COLOR_END}: " )
job_title = input(f"Job Title {COLOR_GREEN}(Can be changed later){COLOR_END}: ") 
given_name = input(f"Given Name {COLOR_GREEN}(Can be changed later){COLOR_END}: ")
last_name = input(f"Last Name {COLOR_GREEN}(Can be changed later){COLOR_END}: ")
email_address = input(f"Email Address {COLOR_GREEN}(Can be changed later){COLOR_END}: ") # Double check this
profile_picture = input(f"Profile Picture URL: {COLOR_YELLOW}(Dashboard > User Management > Your Name > Identity Provider Attributes){COLOR_END}: ")

user_sql = f"INSERT INTO \"User\" (\"Auth0Id\", \"JobTitle\", \"DisplayName\", \"GivenName\", \"LastName\", \"EmailAddress\", \"ProfilePicture\", \"OrganizationId\", \"Created\", \"Modified\") VALUES ('{user_id}', '{job_title}', '{given_name} {last_name}', '{given_name}', '{last_name}', '{email_address}', '{profile_picture}', '{organization_id}', NOW(), NOW());\n"

# User roles
user_roles_sql = """
INSERT INTO "Role" ("Name", "UserId", "Created", "Modified") VALUES ('organization administrator', 1, NOW(), NOW());
INSERT INTO "Role" ("Name", "UserId", "Created", "Modified") VALUES ('sio', 1, NOW(), NOW());
INSERT INTO "Role" ("Name", "UserId", "Created", "Modified") VALUES ('user', 1, NOW(), NOW());
"""

# User settings
user_settings_sql = "INSERT INTO \"UserSettings\" (\"UserId\", \"TimeZone\", \"DateFormat\", \"TimeFormat\", \"Locale\", \"Created\", \"Modified\") VALUES (1, 'GMT Standard Time', 'dddd dd MMMM yyyy', 'HH:mm:ss', 'en-GB', NOW(), NOW());\n"

# Organization settings
organization_settings_sql = f"INSERT INTO \"OrganizationSettings\" (\"OrganizationId\", \"S3Endpoint\", \"S3BucketName\", \"S3NetworkEncryption\", \"S3AccessKey\", \"S3SecretKey\", \"MeilisearchUrl\", \"MeilisearchApiKey\", \"Created\", \"Modified\") VALUES ('{organization_id}', 's3.{root_domain}:9000', 'lighthouse-notes', true, 'CHANGME', 'CHANGEME', 'http://meilisearch:7700', 'CHANGME', NOW(), NOW());\n"

with open(f'init.sql', 'a') as sql_file:
    sql_file.write(organization_sql)
    sql_file.write(user_sql)
    sql_file.write(user_roles_sql)
    sql_file.write(user_settings_sql)
    sql_file.write(organization_settings_sql)

# Final
print (f"Meilisearch API key is: {meilisearch_master_key}")
print (f"\n{COLOR_GREEN}docker-compose.yml file, nginx configurations and initialization database script successfully created!{COLOR_END}\n")