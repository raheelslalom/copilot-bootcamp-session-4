"""SQLAlchemy models for the capabilities management system"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from src.db import Base


# Association table for many-to-many relationship between consultants and capabilities
consultant_capability = Table(
    'consultant_capability',
    Base.metadata,
    Column('consultant_id', Integer, ForeignKey('consultant.id'), primary_key=True),
    Column('capability_id', Integer, ForeignKey('capability.id'), primary_key=True)
)


class Consultant(Base):
    """Represents a consultant who can register for capabilities"""
    __tablename__ = "consultant"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship to capabilities
    capabilities = relationship(
        "Capability",
        secondary=consultant_capability,
        back_populates="consultants"
    )


class Capability(Base):
    """Represents a consulting capability that consultants can register for"""
    __tablename__ = "capability"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    practice_area = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    
    # Store lists as JSON for simplicity (can be normalized later)
    skill_levels = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    industry_verticals = Column(JSON, default=list)
    
    # Relationship to consultants
    consultants = relationship(
        "Consultant",
        secondary=consultant_capability,
        back_populates="capabilities"
    )
