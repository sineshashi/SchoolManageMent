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
    "PASSWORD": "sms@dev", #Local
    # "PASSWORD": "QnulMOBI88621M7wkTSHw4E4QnTeM7jh", #Prod
    "PORT": 5432,
    "HOST": "localhost"
}
#local
# DBURL = "postgres://"+DB_CONFIG["USER"]+":"+DB_CONFIG["PASSWORD"]+"@"+DB_CONFIG["HOST"]+":"+str(DB_CONFIG["PORT"])+"/"+DB_CONFIG["DBNAME"]

#prod
DBURL = "postgres://sms_dev:QnulMOBI88621M7wkTSHw4E4QnTeM7jh@dpg-ccem9kun6mpt4gqtf15g-a.singapore-postgres.render.com/smsdb"

DEPLOYMENT_DETAILS = {
    "HOST": "0.0.0.0",
    "PORT": 10000
}