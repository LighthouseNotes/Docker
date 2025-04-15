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
print("Please enter the requested data at each prompt and press enter.\n")

root_domain = input(f"Root domain (e.g., {COLOR_BLUE}example.com{COLOR_END}): ")

#############
# Generated #
#############
# Database
api_database_password = secrets.token_urlsafe(14)
keycloak_database_password = secrets.token_urlsafe(14)

# Meilisearch
meilisearch_master_key = secrets.token_urlsafe(42)  

##########
# Server #
##########
# Authentication
compose["services"]["server"]["environment"]["Authentication__Authority"] = f"https://idp.{root_domain}"

# Connection string
compose["services"]["server"]["environment"]["ConnectionStrings__Database"] = f"Host=postgresql;Database=lighthousenotes;Username=lighthousenotes;Password={api_database_password}"

# Sqids
compose["services"]["server"]["environment"]["Sqids__Alphabet"] = shuffled_alphabet() 

# Minio
compose["services"]["server"]["environment"]["Minio__Endpoint"] = f"https://s3.{root_domain}"
compose["services"]["server"]["environment"]["Meilisearch__Key"] = meilisearch_master_key


########
# SWAG #
########
compose["services"]["swag"]["environment"]["URL"] = root_domain

############
# Postgres #
############
compose["services"]["database"]["environment"]["POSTGRES_ROOT_PASSWORD"] = secrets.token_urlsafe(14)

############
# Keycloak #
############
compose["services"]["keycloak"]["environment"]["KC_DB_PASSWORD"] = keycloak_database_password
compose["services"]["keyclaok"]["environment"]["KC_HOSTNAME"] = f"https://idp.{root_domain}"
compose["services"]["keyclaok"]["environment"]["KEYCLOAK_ADMIN"] = getpass(f"Keycloak admin password {COLOR_GREEN}(input will not show){COLOR_END}: ")

#########
# Minio #
#########
# Certificate volumes
compose["services"]["minio"]["volumes"][1] = f"./data/swag/etc/letsencrypt/live/api.{root_domain}/fullchain.pem:/root/.minio/certs/public.crt"
compose["services"]["minio"]["volumes"][2] = f"./data/swag/etc/letsencrypt/live/api.{root_domain}/privkey.pem:/root/.minio/certs/private.key"
compose["services"]["minio"]["volumes"][3] = f"./data/swag/etc/letsencrypt/live/api.{root_domain}/fullchain.pem:/root/.minio/certs/CAs/public.crt"
compose["services"]["minio"]["volumes"][4] = f"./data/swag/etc/letsencrypt/live/api.{root_domain}/privkey.pem:/root/.minio/certs/CAs/private.key"


compose["services"]["minio"]["environment"]["MINIO_SERVER_URL"] = f"https://s3.{root_domain}"
compose["services"]["minio"]["environment"]["MINIO_ROOT_PASSWORD"] = getpass(f"Minio root password {COLOR_GREEN}(input will not show){COLOR_END}: ")

###############
# Meilisearch #
###############
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

shutil.move(f'site-confs/idp.example.com.conf', f'site-confs/idp.{root_domain}.conf')
with open(f'site-confs/idp.{root_domain}.conf', 'r+') as api_site_config:
    data = api_site_config.read()
    api_site_config.seek(0)
    data = data.replace('example.com', root_domain)
    api_site_config.write(data)
    api_site_config.truncate()

#######
# SQL #
#######
keycloak_create_sql = f"""
create database keycloak;
create user keycloak with encrypted password '{keycloak_database_password}';
grant all privileges on database keycloak to keycloak;
ALTER DATABASE keycloak OWNER TO keycloak;
"""


lighthousenotes_create_sql = f"""
create database lighthousenotes;
create user lighthousenotes with encrypted password '{api_database_password}';
grant all privileges on database lighthousenotes to lighthousenotes;
ALTER DATABASE lighthousenotes OWNER TO lighthousenotes;
"""

with open('sample.init.sql', 'r') as sql_file:
    existing_content = sql_file.read()

# Write new content followed by the existing content
with open('init.sql', 'w') as sql_file:
    sql_file.write(keycloak_create_sql)
    sql_file.write(lighthousenotes_create_sql)
    sql_file.write(existing_content)

# Final
print (f"Meilisearch API key is: {meilisearch_master_key}")
print (f"\n{COLOR_GREEN}docker-compose.yml file and NGINX configurations created!\n")