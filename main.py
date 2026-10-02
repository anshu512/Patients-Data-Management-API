from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open("patients.json",'r') as f:
        data = json.load(f)
    return data

@app.get("/")
def home():
    return {'message':"Patients Management API"}

@app.get("/about")
def about():
    return {'message':'A fully functional API to manage patients data.'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/view/{patient_id}')
def patient(patient_id:int = Path(...,description="Id of the Patient in DB")):
    data = load_data()
    for p in data:
        if p['patient_id']==patient_id:
            return p
        
    raise HTTPException(status_code=404, detail='Patient NOT Found')

@app.get('/sort')
def sort_patient(sortby:str= Query(...,descripton = "sort by name, age, gender etc"),
                 orderby:str= Query('asc',description="sort by acs or desc order")):
    valid_fields = ['name', 'age', 'gender', 'city']
    if sortby not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field select form {valid_fields}")
    if orderby not in ['asc','desc']:
        raise HTTPException(status_code=400, detail=f"Invalid order select asc or desc")
    
    data = load_data()
    data.sort(
        key=lambda patient: patient[sortby],
        reverse=(orderby == "desc")
    )
    return data