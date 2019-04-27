# spotify-backend - Backend for a collaborative playlist webapp

## Install
```
pip install -r requirements.txt```
export SPOTIFY_KEY=[spotify_api_key_here]
export SECRET_KEY=[flask_secret_key_here]
```

## Run
Debug configuration at: ```./debug```

Prod configuration at: ```gunicorn -c gunicorn.py rest_api.wsgi:app```

Ensure certs for https exist at:
```
certs/privkey.pem
certs/cert.pem
certs/chain.pem
```


## Redis
Install ```redis-server```

Navigate to 'redis' and run: ```redis-server redis.conf```
