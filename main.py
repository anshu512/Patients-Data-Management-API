from fastapi import FastAPI, Path, HTTPException, Query
import json
from pydantic import BaseModel

app = FastAPI()

class Patient(BaseModel):
    name: str
    city: str
    age: int
    gender: str
    height: float  # Fixed typo and changed to float for decimals (e.g., 162.5)
    weight: float  # Changed to float
    diagnosis: str
    phoneNo: str
    email: str

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