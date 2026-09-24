from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, get_db
from app.models import Student
from app.schema import StudentCreate,StudentUpdate


Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "Message": "Student management API is running ✅"
    }


@app.get("/health")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "Success",
            "message": "Database working ✅"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = (
        db.query(Student)
        .filter(Student.email == student.email)
        .first()
    )

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Email already Exists"
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "Message": "Student created Done ✅",
        "student": {
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email,
            "age": new_student.age,
        }
    }


@app.get("/students")
def get_students(
    db: Session = Depends(get_db)
):
    students = db.query(Student).all()

    return {
        "message": "Students fetched successfully",
        "students": [
            {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "age": student.age
            }
            for student in students
        ]
    }

@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
):
    # Find student by ID
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    # Student does not exist
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Check whether another student already uses this email
    existing_email = (
        db.query(Student)
        .filter(
            Student.email == student_data.email,
            Student.id != student_id
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Update values
    student.name = student_data.name
    student.email = student_data.email
    student.age = student_data.age

    # Save to MySQL
    db.commit()
    db.refresh(student)

    return {
        "message": "Student updated successfully",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "age": student.age
        }
    }