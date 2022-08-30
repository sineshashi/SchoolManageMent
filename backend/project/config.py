DOCS_ENABLED = True

CORS_CONFIG = {
    "ALLOWED_HOSTS": ["http://localhost:8000"],
    "ALLOWED_METHODS": ["*"],
    "EXPOSE_HEADERS": ["set-cookie"],
    "ALLOWED_HEADERS": ["*"],
    "ALLOWED_CREDENTIALS": True
}

DB_CONFIG = {
    "USER": "sms_dev",
    "DBNAME": "smsdb",
    "PASSWORD": "sms@dev",
    "PORT": 5432,
    "HOST": "localhost"
}

DBURL = "postgres://"+DB_CONFIG["USER"]+":"+DB_CONFIG["PASSWORD"]+"@"+DB_CONFIG["HOST"]+":"+str(DB_CONFIG["PORT"])+"/"+DB_CONFIG["DBNAME"]

DEPLOYMENT_DETAILS = {
    "HOST": "localhost",
    "PORT": 8080
}