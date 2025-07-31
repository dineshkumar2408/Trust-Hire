from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import jwt
import hashlib
import os
from enum import Enum as PyEnum
import pandas as pd
from io import BytesIO

# FastAPI app initialization
app = FastAPI(
    title="Digiverifier API",
    description="Digital Employment Verification API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./digiverifier.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Enums
class CandidateStatus(PyEnum):
    INVITATION_SENT = "Invitation Email Sent"
    DL_PENDING = "DL Pending"
    ITR_PENDING = "ITR Pending"
    EPFO_PENDING = "EPFO Pending"
    EVF_PENDING = "EVF Pending"
    QC_PENDING = "QC Process Pending"
    COMPLETED = "Completed"
    BILLED = "Billed"
    INVITATION_EXPIRED = "Invitation Expired"
    PROCESS_DECLINED = "Process Declined"

class ReportStatus(PyEnum):
    DIGITAL_REPORT = "Digital Report"
    PROCESS_DECLINED = "Process Declined"

class VerificationMode(PyEnum):
    DIGITAL = "Digital"
    CONVENTIONAL = "Conventional"
    HYBRID = "Hybrid"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    contact_number = Column(String)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    contact_number = Column(String)
    service_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    dv_id = Column(String, unique=True, index=True)
    applicant_id = Column(String, index=True)
    name = Column(String, index=True)
    email = Column(String)
    mobile_number = Column(String)
    date_of_birth = Column(DateTime)
    status = Column(String, default=CandidateStatus.INVITATION_SENT.value)
    report_status = Column(String, default=ReportStatus.DIGITAL_REPORT.value)
    mode = Column(String, default=VerificationMode.DIGITAL.value)
    client_id = Column(Integer, ForeignKey("clients.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    client = relationship("Client", back_populates="candidates")
    verifications = relationship("Verification", back_populates="candidate")

class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    verification_type = Column(String)  # DL, ITR, EPFO, EVF, QC
    status = Column(String, default="Pending")
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    result = Column(Text)
    
    candidate = relationship("Candidate", back_populates="verifications")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    report_type = Column(String)
    file_path = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate")

class CallerLog(Base):
    __tablename__ = "caller_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String)
    candidate_name = Column(String)
    email = Column(String)
    mobile_number = Column(String)
    candidate_status = Column(String)
    status = Column(String, default="NOT_AVAILABLE")
    comment = Column(String, default="NOT_AVAILABLE")
    created_at = Column(DateTime, default=datetime.utcnow)

# Add relationships
Client.candidates = relationship("Candidate", back_populates="client")

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CandidateCreate(BaseModel):
    applicant_id: str
    name: str
    email: EmailStr
    mobile_number: str
    date_of_birth: Optional[datetime] = None
    client_id: int

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    status: Optional[str] = None

class DashboardStats(BaseModel):
    invitation_expired: int
    pending_status: dict
    report_status: dict
    upload_volume: int
    company_name: str

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Routes

@app.get("/")
async def root():
    return {"message": "Digiverifier API - Digital Employment Verification System"}

# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create token
    access_token = create_access_token({"sub": user.email, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Verify user
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token({"sub": user.email, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# Dashboard endpoints
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(verify_token)):
    # Calculate stats based on the UI
    total_candidates = db.query(Candidate).count()
    invitation_expired = db.query(Candidate).filter(Candidate.status == CandidateStatus.INVITATION_EXPIRED.value).count()
    
    # Pending status counts
    dl_pending = db.query(Candidate).filter(Candidate.status == CandidateStatus.DL_PENDING.value).count()
    itr_pending = db.query(Candidate).filter(Candidate.status == CandidateStatus.ITR_PENDING.value).count()
    epfo_pending = db.query(Candidate).filter(Candidate.status == CandidateStatus.EPFO_PENDING.value).count()
    evf_pending = db.query(Candidate).filter(Candidate.status == CandidateStatus.EVF_PENDING.value).count()
    qc_pending = db.query(Candidate).filter(Candidate.status == CandidateStatus.QC_PENDING.value).count()
    
    # Report status counts
    digital_reports = db.query(Candidate).filter(Candidate.report_status == ReportStatus.DIGITAL_REPORT.value).count()
    process_declined = db.query(Candidate).filter(Candidate.report_status == ReportStatus.PROCESS_DECLINED.value).count()
    
    return DashboardStats(
        invitation_expired=invitation_expired,
        pending_status={
            "dl_pending": dl_pending,
            "itr_pending": itr_pending,
            "epfo_pending": epfo_pending,
            "evf_pending": evf_pending,
            "qc_pending": qc_pending
        },
        report_status={
            "digital_report": digital_reports,
            "process_declined": process_declined
        },
        upload_volume=total_candidates,
        company_name="Crossbow Global Marketplace Solutions Pvt Ltd"
    )

# Candidate Management endpoints
@app.get("/candidates")
async def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    query = db.query(Candidate)
    
    if search:
        query = query.filter(
            (Candidate.name.contains(search)) |
            (Candidate.email.contains(search)) |
            (Candidate.applicant_id.contains(search))
        )
    
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    
    candidates = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "candidates": candidates,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/candidates")
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    # Generate DV ID
    count = db.query(Candidate).count()
    dv_id = f"DV_{count + 1}"
    
    db_candidate = Candidate(
        dv_id=dv_id,
        applicant_id=candidate.applicant_id,
        name=candidate.name,
        email=candidate.email,
        mobile_number=candidate.mobile_number,
        date_of_birth=candidate.date_of_birth,
        client_id=candidate.client_id
    )
    
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate

@app.put("/candidates/{candidate_id}")
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    db_candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    update_data = candidate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_candidate, field, value)
    
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.post("/candidates/upload")
async def upload_candidates(
    file: UploadFile = File(...),
    client_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Only Excel and CSV files are supported")
    
    try:
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))
        
        candidates_created = []
        for _, row in df.iterrows():
            count = db.query(Candidate).count()
            dv_id = f"DV_{count + 1}"
            
            db_candidate = Candidate(
                dv_id=dv_id,
                applicant_id=row.get('applicant_id', ''),
                name=row.get('name', ''),
                email=row.get('email', ''),
                mobile_number=str(row.get('mobile_number', '')),
                client_id=client_id
            )
            
            db.add(db_candidate)
            candidates_created.append(db_candidate)
        
        db.commit()
        return {"message": f"Successfully uploaded {len(candidates_created)} candidates"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

# Verification endpoints
@app.post("/candidates/{candidate_id}/verify/{verification_type}")
async def initiate_verification(
    candidate_id: int,
    verification_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    verification = Verification(
        candidate_id=candidate_id,
        verification_type=verification_type.upper(),
        status="Pending"
    )
    
    db.add(verification)
    
    # Update candidate status
    status_map = {
        "DL": CandidateStatus.DL_PENDING.value,
        "ITR": CandidateStatus.ITR_PENDING.value,
        "EPFO": CandidateStatus.EPFO_PENDING.value,
        "EVF": CandidateStatus.EVF_PENDING.value,
        "QC": CandidateStatus.QC_PENDING.value
    }
    
    if verification_type.upper() in status_map:
        candidate.status = status_map[verification_type.upper()]
    
    db.commit()
    db.refresh(verification)
    
    return {"message": f"{verification_type} verification initiated", "verification": verification}

# Reports endpoints
@app.get("/reports")
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    query = db.query(Candidate)
    
    if from_date:
        query = query.filter(Candidate.uploaded_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Candidate.uploaded_at <= datetime.fromisoformat(to_date))
    
    reports = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "reports": reports,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.get("/reports/export")
async def export_reports(
    format: str = Query("xlsx", regex="^(xlsx|csv)$"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    query = db.query(Candidate)
    
    if from_date:
        query = query.filter(Candidate.uploaded_at >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Candidate.uploaded_at <= datetime.fromisoformat(to_date))
    
    candidates = query.all()
    
    # Convert to DataFrame
    data = []
    for candidate in candidates:
        data.append({
            "DV_ID": candidate.dv_id,
            "Applicant_ID": candidate.applicant_id,
            "Name": candidate.name,
            "Email": candidate.email,
            "Mobile_Number": candidate.mobile_number,
            "Status": candidate.status,
            "Mode": candidate.mode,
            "Date_of_Birth": candidate.date_of_birth,
            "Uploaded_At": candidate.uploaded_at
        })
    
    df = pd.DataFrame(data)
    
    if format == "csv":
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return {"download_url": "/download/reports.csv", "file_size": len(output.getvalue())}
    else:
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return {"download_url": "/download/reports.xlsx", "file_size": len(output.getvalue())}

# Caller Management endpoints
@app.get("/caller-logs")
async def get_caller_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    logs = db.query(CallerLog).offset(skip).limit(limit).all()
    total = db.query(CallerLog).count()
    
    return {
        "logs": logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/caller-logs")
async def create_caller_log(
    applicant_id: str,
    candidate_name: str,
    email: str,
    mobile_number: str,
    candidate_status: str,
    status: str = "NOT_AVAILABLE",
    comment: str = "NOT_AVAILABLE",
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    caller_log = CallerLog(
        applicant_id=applicant_id,
        candidate_name=candidate_name,
        email=email,
        mobile_number=mobile_number,
        candidate_status=candidate_status,
        status=status,
        comment=comment
    )
    
    db.add(caller_log)
    db.commit()
    db.refresh(caller_log)
    
    return caller_log

# Client Management endpoints
@app.get("/clients")
async def get_clients(db: Session = Depends(get_db), current_user = Depends(verify_token)):
    return db.query(Client).all()

@app.post("/clients")
async def create_client(
    name: str,
    email: str,
    contact_number: str,
    address: str,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    client = Client(
        name=name,
        email=email,
        contact_number=contact_number,
        address=address
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client

# Vendor Management endpoints
@app.get("/vendors")
async def get_vendors(db: Session = Depends(get_db), current_user = Depends(verify_token)):
    return db.query(Vendor).all()

@app.post("/vendors")
async def create_vendor(
    name: str,
    email: str,
    contact_number: str,
    service_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    vendor = Vendor(
        name=name,
        email=email,
        contact_number=contact_number,
        service_type=service_type
    )
    
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    
    return vendor

# UAN Search endpoint
@app.get("/uan-search")
async def search_uan(
    uan: str = Query(..., min_length=12, max_length=12),
    db: Session = Depends(get_db),
    current_user = Depends(verify_token)
):
    # This would integrate with actual UAN verification service
    # For now, return mock data
    return {
        "uan": uan,
        "name": "John Doe",
        "status": "Active",
        "member_id": "101234567890",
        "establishment": "ABC Company Pvt Ltd"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)