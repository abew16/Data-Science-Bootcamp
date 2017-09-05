import requests

resp = requests.get('https://httpbin.org/ip')
print(resp)
