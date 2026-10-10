from fastapi import FastAPI, Path, HTTPException, Query
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Emailstr

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='Id of patient')]
    name: Annotated[str, Field(..., description='name of patient')]
    city: Annotated[str, Field(..., description='City of person')]
    age: Annotated[int, Field(..., gt = 0, description='Age of the patient')]
    gender: Annotated[Literal['Male','Female','others'], Field(..., description='Gender of the person')]
    height: Annotated[float, Field(..., gt = 0, description='Height of the patient in meters.')]
    weight: Annotated[float, Field(..., gt = 0, description='weight of the patient in kg.')]
    diagnosis: Annotated[str, Field(..., descriotion='Disease of the patient')]
    phone: str = Field(..., pattern=r"^\+91-\d{10}$",description="Indian phone number in +91-XXXXXXXXXX format")
    email: Emailstr = Field( description='Email of the patient')
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight / self.height**2),2)
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
        

def load_data():
    with open("patients.json", 'r') as f:
        data = json.load(f)
    return data

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
    
    # Since data is a dictionary, we can just check if the ID exists as a key
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
    
    # Convert the dictionary values into a list so they can be sorted
    patients_list = list(data.values())
    
    patients_list.sort(
        key=lambda patient: patient[sortby],
        reverse=(orderby == "desc")
    )
    return patients_list