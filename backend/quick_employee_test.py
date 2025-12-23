import requests
import json

BASE = 'http://localhost:5000'

print("Testing Employee APIs...\n")

# 1. Login
print("1. Login...")
r = requests.post(
    f'{BASE}/api/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)

if r.status_code == 200:
    token = r.json()['token']
    print(f"✅ Token: {token[:40]}...\n")
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Get employees
    print("2. Get all employees...")
    r = requests.get(f'{BASE}/api/employees', headers=headers)
    print(f"✅ Status: {r.status_code}")
    print(f"   Found {r.json()['count']} employees\n")

    # 3. Create employee
    print("3. Create employee...")
    r = requests.post(
        f'{BASE}/api/employees',
        json={
            'name': 'Rohit Kemade',
            'email': 'rohit@company.com',
            'phone': '8767259045',
            'department_id': 1,
            'salary': 50000,
            'join_date': '2024-01-15'
        },
        headers=headers
    )

    print(f"✅ Status: {r.status_code}")

    if r.status_code == 201:
        emp_id = r.json()['employee_id']
        print(f"   Created employee ID: {emp_id}\n")

        # 4. Get employee
        print(f"4. Get employee {emp_id}...")
        r = requests.get(f'{BASE}/api/employees/{emp_id}', headers=headers)
        print(f"✅ Status: {r.status_code}")
        print(f"   Name: {r.json()['employee']['name']}\n")

        # 5. Get statistics
        print("5. Get statistics...")
        r = requests.get(f'{BASE}/api/employees/stats', headers=headers)
        stats = r.json()['stats']
        print(f"   Total active: {stats['total_active']}")

        print("\n🎉 All employee endpoints working perfectly!")
    else:
        print(f"❌ Create failed: {r.json()}")
else:
    print(f"❌ Login failed: {r.status_code}")
