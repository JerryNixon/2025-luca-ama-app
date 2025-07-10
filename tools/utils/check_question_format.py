import requests
import json

# Login and get questions to see the format
BASE_URL = 'http://127.0.0.1:8000/api'
EVENT_ID = 'abe6ad88-b6ff-4cc6-9f83-2003e54c69bb'

# Login as Jerry
response = requests.post(f'{BASE_URL}/auth/login/', json={
    'email': 'jerry.nixon@microsoft.com',
    'password': 'test123'
})

if response.status_code == 200:
    token = response.json()['data']['token']
    
    # Get questions
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/events/{EVENT_ID}/questions/', headers=headers)
    
    if response.status_code == 200:
        questions = response.json()
        print('First question data:')
        print(json.dumps(questions[0] if questions else {}, indent=2))
    else:
        print('Failed to get questions:', response.text)
else:
    print('Login failed:', response.text)
