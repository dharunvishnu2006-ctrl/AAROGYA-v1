import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')

cities = ['Chennai','Mumbai','Delhi','Bangalore','Hyderabad','Kolkata','Pune','Ahmedabad','Jaipur','Lucknow']
genders = ['Male','Female']

rows = []
for i in range(1,51):
    gender = random.choice(genders)
    age = random.randint(18, 75)
    bmi = round(random.uniform(17.0,40.0),1)

    rows.append({
        'patient_id':f'P{i:03d}',
        'name': fake.name_male() if gender == 'Male' else fake.name_female(),
        'age': age,
        'gender':gender,
        'bmi': bmi,
        'bp_systolic': random.randint(100,190),
        'bp_diastolic': random.randint(60,110),
        'sugar_fasting': random.randint(70,250),
        'city': random.choice(cities) 
    })

df = pd.DataFrame(rows)
df.to_csv('data/patients_sample.csv', index=False)
print(f'Generated {len(df)} patients')