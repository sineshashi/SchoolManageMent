DOCS_ENABLED = True
ENV = "prod"

CORS_CONFIG = {
    "ALLOWED_HOSTS": ["*"],
    "ALLOWED_METHODS": ["*"],
    "EXPOSE_HEADERS": ["set-cookie"],
    "ALLOWED_HEADERS": ["*"],
    "ALLOWED_CREDENTIALS": True
}

DB_CONFIG = {
    "USER": "sms_dev",
    "DBNAME": "smsdb",
    "PASSWORD": "sms@dev", #Local
    # "PASSWORD": "QnulMOBI88621M7wkTSHw4E4QnTeM7jh", #Prod
    "PORT": 5432,
    "HOST": "localhost"
}
if ENV == "local":
    DBURL = "postgres://"+DB_CONFIG["USER"]+":"+DB_CONFIG["PASSWORD"]+"@"+DB_CONFIG["HOST"]+":"+str(DB_CONFIG["PORT"])+"/"+DB_CONFIG["DBNAME"]
    MIGRATION_LOCATION = "./local_migrations"

elif ENV == "prod":
    DBURL = "postgres://sms_dev:QnulMOBI88621M7wkTSHw4E4QnTeM7jh@dpg-ccem9kun6mpt4gqtf15g-a.singapore-postgres.render.com/smsdb"
    MIGRATION_LOCATION = "./prod_migrations"

DEPLOYMENT_DETAILS = {
    "HOST": "0.0.0.0",
    "PORT": 10000
}

if ENV == "local":
    ALLOW_SELF_ONBOARDING = True
elif ENV == "prod":
    ALLOW_SELF_ONBOARDING = False