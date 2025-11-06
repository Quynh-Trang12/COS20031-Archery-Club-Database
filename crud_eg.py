from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db_config import get_engine
from models import Archer, Gender, Division, Session, Round # Import your models
import datetime

# --- 1. Setup ---
# Get the engine
engine = get_engine()

# Create a Session "factory"
# This binds your engine to the Session object
SessionLocal = sessionmaker(bind=engine)

# --- 2. Create Data (INSERT) ---
def create_archer():
    print("--- CREATING ARCHER ---")
    # A session is a temporary "workspace" for your data
    with SessionLocal() as session:
        
        # You query for existing objects (like Gender)
        # Assuming 'M' and 'R' were pre-loaded into your DB
        gender_m = session.execute(select(Gender).where(Gender.gender_code == 'M')).scalar_one_or_none()
        div_r = session.execute(select(Division).where(Division.bow_type_code == 'R')).scalar_one_or_none()

        if not gender_m:
            print("Gender 'M' not found. Adding it.")
            gender_m = Gender(gender_code='M')
            session.add(gender_m)

        if not div_r:
            print("Division 'R' not found. Adding it.")
            div_r = Division(bow_type_code='R', is_active=True)
            session.add(div_r)
        
        # Create a new Python object
        new_archer = Archer(
            birth_year=2000,
            gender=gender_m,      # Pass the whole object!
            division=div_r      # Pass the whole object!
        )
        
        # Add it to the session
        session.add(new_archer)
        
        # Commit the transaction to save it to the DB
        session.commit()
        
        print(f"Created new archer with ID: {new_archer.id}")
        return new_archer.id

# --- 3. Read Data (SELECT) ---
def read_archer(archer_id):
    print(f"\n--- READING ARCHER {archer_id} ---")
    with SessionLocal() as session:
        # Build a query
        statement = select(Archer).where(Archer.id == archer_id)
        
        # Execute and get the result
        # .scalar_one() gets the single Archer object, or raises an error if not found
        archer = session.execute(statement).scalar_one()
        
        if archer:
            print(f"Found Archer: ID={archer.id}, Year={archer.birth_year}")
            # You can access related objects directly!
            print(f"  Gender: {archer.gender.gender_code}")
            print(f"  Division: {archer.division.bow_type_code}")
        else:
            print("Archer not found.")

# --- 4. Update Data (UPDATE) ---
def update_archer(archer_id):
    print(f"\n--- UPDATING ARCHER {archer_id} ---")
    with SessionLocal() as session:
        # First, get the archer
        statement = select(Archer).where(Archer.id == archer_id)
        archer_to_update = session.execute(statement).scalar_one()
        
        if archer_to_update:
            # Simply change the Python object's attribute
            archer_to_update.birth_year = 2001
            
            # Commit the session to save the change
            session.commit()
            print("Archer updated.")
        else:
            print("Archer not found.")

# --- 5. Delete Data (DELETE) ---
def delete_archer(archer_id):
    print(f"\n--- DELETING ARCHER {archer_id} ---")
    with SessionLocal() as session:
        # Get the archer
        statement = select(Archer).where(Archer.id == archer_id)
        archer_to_delete = session.execute(statement).scalar_one()
        
        if archer_to_delete:
            # Delete the object
            session.delete(archer_to_delete)
            
            # Commit the change
            session.commit()
            print("Archer deleted.")
        else:
            print("Archer not found.")


if __name__ == "__main__":
    # Run the examples
    new_id = create_archer()
    read_archer(new_id)
    update_archer(new_id)
    read_archer(new_id) # Read again to see the change
    delete_archer(new_id)