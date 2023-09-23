import requests

url = 'http://127.0.0.1:18080'

def visit(endpoint):
    r = requests.post(url + endpoint)
    # print(r.text)
    
if __name__ == '__main__':
    for i in range(1000):
        visit('/hello')
    visit('/stop')