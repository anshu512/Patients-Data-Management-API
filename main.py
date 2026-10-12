from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field, EmailStr
from typing import Annotated, Literal, Optional

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='Id of patient')]
    name: Annotated[str, Field(..., description='name of patient')]
    city: Annotated[str, Field(..., description='City of person')]
    age: Annotated[int, Field(..., gt=0, description='Age of the patient')]
    gender: Annotated[Literal['Male', 'Female', 'Others'], Field(..., description='Gender of the person')] # Fixed capitalization
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in meters.')]
    weight: Annotated[float, Field(..., gt=0, description='weight of the patient in kg.')]
    diagnosis: Annotated[str, Field(..., description='Disease of the patient')] # Fixed 'descriotion' typo
    phone: str = Field(..., pattern=r"^\+91-\d{10}$", description="Indian phone number in +91-XXXXXXXXXX format")
    email: EmailStr = Field(description='Email of the patient')
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight / self.height**2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Under-weight"
        elif self.bmi < 30:
            return "Normal"
        else:
            return "Over-weight"

class Patientupdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'Others']], Field(default=None)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    city: Annotated[Optional[str], Field(default=None)]

def load_data():
    with open("patients.json", 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json", 'w') as f:
        json.dump(data, f, indent=4) # Added indent for readable JSON saving

@app.get("/")
def home():
    return {'message': "Patients Management API"}

@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage patients data.'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/view/{patient_id}')
def patient(patient_id: str = Path(..., description="Id of the Patient in DB (e.g., P001)")):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
        
    raise HTTPException(status_code=404, detail='Patient NOT Found')

@app.get('/sort')
def sort_patient(
    sortby: str = Query(..., description="sort by name, age, gender etc"),
    orderby: str = Query('asc', description="sort by asc or desc order")
):
    valid_fields = ['name', 'age', 'gender', 'city', 'weight', 'height']
    if sortby not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field select from {valid_fields}")
    if orderby not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order select asc or desc")
    
    data = load_data()
    
    patients_list = list(data.values())
    
    patients_list.sort(
        key=lambda patient: patient[sortby],
        reverse=(orderby == "desc")
    )
    return patients_list

@app.post('/create')
def create_patient(patient: Patient):
    data = load_data()
    
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    else:
        # Changed to set syntax for exclude
        data[patient.id] = patient.model_dump(exclude={'id'}) 
        save_data(data)
        
    return JSONResponse(status_code=201, content={'message': 'Patient Created Successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: Patientupdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient did not exist.')
    
    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)
    
    # FIXED: Added .items() to iterate dictionary
    for key, value in updated_patient_info.items(): 
        existing_patient_info[key] = value 
        
    # FIXED: Added quotes around 'id'
    existing_patient_info['id'] = patient_id 
    
    patient_pydantic_obj = Patient(**existing_patient_info)
    
    # FIXED: Changed exclude syntax to a set
    existing_patient_info = patient_pydantic_obj.model_dump(exclude={'id'}) 
    data[patient_id] = existing_patient_info
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message': 'Patient Updated'})