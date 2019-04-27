import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

keyfile = 'certs/privkey.pem'
certfile = 'certs/cert.pem'
ca_certs = 'certs/chain.pem'
