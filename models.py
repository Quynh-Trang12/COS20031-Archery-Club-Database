import datetime
from sqlalchemy import (
    create_engine, String, Integer, SmallInteger, Date, Enum, 
    ForeignKey, UniqueConstraint, CheckConstraint, TEXT, CHAR, BOOLEAN
)
from sqlalchemy.dialects.mysql import YEAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# --- 1. Base Class ---
# All our models will inherit from this class
class Base(DeclarativeBase):
    pass

# --- 2. Model Definitions ---
# Based on your archery_db.sql file

class Gender(Base):
    __tablename__ = 'gender'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gender_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # Using String for ENUM
    
    # Relationships
    archers: Mapped[list["Archer"]] = relationship(back_populates="gender")
    categories: Mapped[list["Category"]] = relationship(back_populates="gender")

class Division(Base):
    __tablename__ = 'division'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bow_type_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) # Using String for ENUM
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    
    # Relationships
    archers: Mapped[list["Archer"]] = relationship(back_populates="division")
    categories: Mapped[list["Category"]] = relationship(back_populates="division")

class AgeClass(Base):
    __tablename__ = 'age_class'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    age_class_code: Mapped[str] = mapped_column(String(16), nullable=False)
    min_birth_year: Mapped[int] = mapped_column(YEAR, nullable=False)
    max_birth_year: Mapped[int] = mapped_column(YEAR, nullable=False)
    policy_year: Mapped[int] = mapped_column(YEAR, nullable=False)
    
    # Relationships
    categories: Mapped[list["Category"]] = relationship(back_populates="age_class")
    
    __table_args__ = (UniqueConstraint('age_class_code', 'policy_year', name='uk_age_class_policy'),)

class Round(Base):
    __tablename__ = 'round'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    
    # Relationships
    sessions: Mapped[list["Session"]] = relationship(back_populates="round")
    round_ranges: Mapped[list["RoundRange"]] = relationship(back_populates="round")

class Archer(Base):
    __tablename__ = 'archer'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    birth_year: Mapped[int] = mapped_column(YEAR, nullable=False)
    
    # Foreign Keys
    gender_id: Mapped[int] = mapped_column(ForeignKey('gender.id'), nullable=False)
    division_id: Mapped[int] = mapped_column(ForeignKey('division.id'), nullable=False)
    
    # Relationships (links to the Python objects)
    gender: Mapped["Gender"] = relationship(back_populates="archers")
    division: Mapped["Division"] = relationship(back_populates="archers")
    sessions: Mapped[list["Session"]] = relationship(back_populates="archer")

class Session(Base):
    __tablename__ = 'session'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    archer_id: Mapped[int] = mapped_column(ForeignKey('archer.id'), nullable=False)
    round_id: Mapped[int] = mapped_column(ForeignKey('round.id'), nullable=False)
    shoot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(255), default='Preliminary', nullable=False) # Using String for ENUM
    
    # Relationships
    archer: Mapped["Archer"] = relationship(back_populates="sessions")
    round: Mapped["Round"] = relationship(back_populates="sessions")
    ends: Mapped[list["End"]] = relationship(back_populates="session")
    competition_entries: Mapped[list["CompetitionEntry"]] = relationship(back_populates="session")

class RoundRange(Base):
    __tablename__ = 'round_range'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(ForeignKey('round.id'), nullable=False)
    distance_m: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    face_size: Mapped[int] = mapped_column(SmallInteger, nullable=False) # Using SmallInt for TINYINT
    ends_per_range: Mapped[int] = mapped_column(SmallInteger, nullable=False) # Using SmallInt for TINYINT
    
    # Relationships
    round: Mapped["Round"] = relationship(back_populates="round_ranges")
    ends: Mapped[list["End"]] = relationship(back_populates="round_range")
    
    __table_args__ = (
        UniqueConstraint('round_id', 'distance_m', 'face_size', name='uk_round_distance'),
        CheckConstraint('face_size IN (80, 122)', name='chk_face_size'),
        CheckConstraint('ends_per_range IN (5, 6)', name='chk_ends_per_range')
    )

class End(Base):
    __tablename__ = 'end'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('session.id'), nullable=False)
    round_range_id: Mapped[int] = mapped_column(ForeignKey('round_range.id'), nullable=False)
    end_no: Mapped[int] = mapped_column(SmallInteger, nullable=False) # Using SmallInt for TINYINT
    
    # Relationships
    session: Mapped["Session"] = relationship(back_populates="ends")
    round_range: Mapped["RoundRange"] = relationship(back_populates="ends")
    arrows: Mapped[list["Arrow"]] = relationship(back_populates="end")
    
    __table_args__ = (
        UniqueConstraint('session_id', 'round_range_id', 'end_no', name='uk_session_range_end'),
        CheckConstraint('end_no BETWEEN 1 AND 6', name='chk_end_no')
    )

class Arrow(Base):
    __tablename__ = 'arrow'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    end_id: Mapped[int] = mapped_column(ForeignKey('end.id'), nullable=False)
    arrow_no: Mapped[int] = mapped_column(SmallInteger, nullable=False) # Using SmallInt for TINYINT
    arrow_value: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    
    # Relationships
    end: Mapped["End"] = relationship(back_populates="arrows")
    
    __table_args__ = (
        UniqueConstraint('end_id', 'arrow_no', name='uk_end_arrow'),
        CheckConstraint('arrow_no BETWEEN 1 AND 6', name='chk_arrow_no'),
        CheckConstraint("arrow_value IN ('X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M')", name='chk_arrow_value')
    )

# --- Define Category, Competition, and CompetitionEntry (as in your SQL) ---
# (I've omitted them here for brevity, but you would add them following the same pattern)
class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    age_class_id: Mapped[int] = mapped_column(ForeignKey('age_class.id'), nullable=False)
    gender_id: Mapped[int] = mapped_column(ForeignKey('gender.id'), nullable=False)
    division_id: Mapped[int] = mapped_column(ForeignKey('division.id'), nullable=False)
    
    # Relationships
    age_class: Mapped["AgeClass"] = relationship(back_populates="categories")
    gender: Mapped["Gender"] = relationship(back_populates="categories")
    division: Mapped["Division"] = relationship(back_populates="categories")
    competition_entries: Mapped[list["CompetitionEntry"]] = relationship(back_populates="category")
    
    __table_args__ = (UniqueConstraint('age_class_id', 'gender_id', 'division_id', name='uk_category_combination'),)

class Competition(Base):
    __tablename__ = 'competition'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    rules_note: Mapped[str] = mapped_column(TEXT, nullable=True)
    
    # Relationships
    competition_entries: Mapped[list["CompetitionEntry"]] = relationship(back_populates="competition")

class CompetitionEntry(Base):
    __tablename__ = 'competition_entry'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('session.id'), nullable=False)
    competition_id: Mapped[int] = mapped_column(ForeignKey('competition.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'), nullable=False)
    final_total: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    rank_in_category: Mapped[int] = mapped_column(SmallInteger, nullable=True) # Using SmallInt for TINYINT
    
    # Relationships
    session: Mapped["Session"] = relationship(back_populates="competition_entries")
    competition: Mapped["Competition"] = relationship(back_populates="competition_entries")
    category: Mapped["Category"] = relationship(back_populates="competition_entries")
    
    __table_args__ = (UniqueConstraint('competition_id', 'session_id', name='uk_competition_session'),)


# --- 3. Utility Function to Create Tables ---
def create_tables(engine):
    """
    Creates all tables defined in Base.metadata.
    This is an alternative to running the .sql file manually.
    """
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    # This block runs only when you execute models.py directly
    # It will create all your tables in the database.
    from db_config import get_engine
    
    print("Connecting to database and creating tables...")
    engine = get_engine()
    create_tables(engine)
    print("Tables created successfully (if they didn't exist).")