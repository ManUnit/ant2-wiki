import urllib.request, json, sys

# Login
data = json.dumps({'username':'admin','password':'Admin@123'}).encode()
req = urllib.request.Request('http://localhost:4000/api/auth/login', data=data,
                              headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read())['token']

# Check monitor overview
with urllib.request.urlopen(f'http://localhost:4000/api/monitor/overview?token={token}') as r:
    d = json.loads(r.read())

redis = d.get('redis')
print('redis field present:', redis is not None)
print(json.dumps(redis, indent=2))
