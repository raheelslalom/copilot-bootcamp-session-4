"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from src.db import init_db, SessionLocal, get_db
from src.models import Capability, Consultant

# Seed data for initial capabilities
INITIAL_CAPABILITIES = [
    {
        "name": "Cloud Architecture",
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
    },
    {
        "name": "Data Analytics",
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
    },
    {
        "name": "DevOps Engineering",
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
    },
    {
        "name": "Digital Strategy",
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
    },
    {
        "name": "Change Management",
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
    },
    {
        "name": "UX/UI Design",
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
    },
    {
        "name": "Cybersecurity",
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
    },
    {
        "name": "Business Intelligence",
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
    },
    {
        "name": "Agile Coaching",
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
    }
]


def seed_database(db: Session):
    """Seed the database with initial capabilities data"""
    for cap_data in INITIAL_CAPABILITIES:
        # Check if capability already exists
        existing = db.query(Capability).filter(Capability.name == cap_data["name"]).first()
        if existing:
            continue

        # Create capability
        capability = Capability(
            name=cap_data["name"],
            description=cap_data["description"],
            practice_area=cap_data["practice_area"],
            skill_levels=cap_data["skill_levels"],
            certifications=cap_data["certifications"],
            industry_verticals=cap_data["industry_verticals"],
            capacity=cap_data["capacity"]
        )
        db.add(capability)
        db.flush()

        # Add consultants for this capability
        for email in cap_data["consultants"]:
            consultant = db.query(Consultant).filter(Consultant.email == email).first()
            if not consultant:
                consultant = Consultant(email=email)
                db.add(consultant)
                db.flush()
            capability.consultants.append(consultant)

    db.commit()


app = FastAPI(title="Slalom Capabilities Management API",
              description="API for managing consulting capabilities and consultant expertise")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup"""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities(db: Session = Depends(get_db)):
    """Get all capabilities with their registered consultants"""
    capabilities = db.query(Capability).all()
    result = {}
    for cap in capabilities:
        result[cap.name] = {
            "description": cap.description,
            "practice_area": cap.practice_area,
            "skill_levels": cap.skill_levels,
            "certifications": cap.certifications,
            "industry_verticals": cap.industry_verticals,
            "capacity": cap.capacity,
            "consultants": [c.email for c in cap.consultants]
        }
    return result


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Register a consultant for a capability"""
    # Validate capability exists
    capability = db.query(Capability).filter(Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Check if consultant is already registered
    existing = db.query(Consultant).filter(Consultant.email == email).first()
    if existing and capability in existing.capabilities:
        raise HTTPException(
            status_code=400,
            detail="Consultant is already registered for this capability"
        )

    # Create consultant if doesn't exist
    if not existing:
        existing = Consultant(email=email)
        db.add(existing)
        db.flush()

    # Add consultant to capability
    existing.capabilities.append(capability)
    db.commit()
    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a consultant from a capability"""
    # Validate capability exists
    capability = db.query(Capability).filter(Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get consultant
    consultant = db.query(Consultant).filter(Consultant.email == email).first()
    if not consultant or capability not in consultant.capabilities:
        raise HTTPException(
            status_code=400,
            detail="Consultant is not registered for this capability"
        )

    # Remove consultant from capability
    consultant.capabilities.remove(capability)
    db.commit()
    return {"message": f"Unregistered {email} from {capability_name}"}
