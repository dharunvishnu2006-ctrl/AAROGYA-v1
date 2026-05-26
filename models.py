class Person:
    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

class Patient(Person):
    def __init__(self,patient_id,name,age,gender,bmi,bp_systolic,bp_diastolic,sugar_fasting,city):
        super().__init__(name,age,gender)
        self.patient_id = patient_id
        self.bmi = bmi
        self.bp_systolic = bp_systolic
        self.bp_diastolic = bp_diastolic
        self.sugar_fasting = sugar_fasting
        self.city = city

    def get_bmi_category(self):
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight' 
        else:
            return 'Obese'

    def is_hypertensive(self):
        return self.bp_systolic > 140
    def is_diabetic(self):
        return self.sugar_fasting > 126      
    
class Doctor(Person):
    def __init__(self, doctor_id, name, 
                 age, gender, specialty, hospital):
        super().__init__(name, age, gender)
        self.doctor_id = doctor_id
        self.specialty = specialty
        self.hospital = hospital
        self.assigned_patients = []

    def add_patient(self, patient):
        self.assigned_patients.append(patient)

    def get_assigned_patients(self):
        return self.assigned_patients
    
class Hospital:

    def __init__(self, hospital_id, name, city, total_beds):
        self.hospital_id = hospital_id
        self.name = name
        self.city = city
        self.total_beds = total_beds

    def occupancy_rate(self, current_patients):
        return round((current_patients /
                      self.total_beds)* 100, 1)        
