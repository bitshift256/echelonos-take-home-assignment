#!/usr/bin/env python3
"""Seed the database with sample data for testing."""
import os
import sys
from datetime import date, timedelta
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Employee, Team, TeamMember, EmployeeStatus


def seed_data():
    """Seed the database with sample employees and teams."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Employee).count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create employees
        employees_data = [
            # CEO (no manager)
            {"employee_id": "EMP001", "first_name": "Sarah", "last_name": "Johnson", 
             "email": "sarah.johnson@company.com", "phone": "+1-555-0101",
             "title": "Chief Executive Officer", "department": "Executive",
             "hire_date": date(2015, 1, 15), "salary": 350000, "manager_id": None},
            
            # C-Suite (report to CEO)
            {"employee_id": "EMP002", "first_name": "Michael", "last_name": "Chen",
             "email": "michael.chen@company.com", "phone": "+1-555-0102",
             "title": "Chief Technology Officer", "department": "Technology",
             "hire_date": date(2016, 3, 1), "salary": 280000, "manager_id": 1},
            {"employee_id": "EMP003", "first_name": "Emily", "last_name": "Rodriguez",
             "email": "emily.rodriguez@company.com", "phone": "+1-555-0103",
             "title": "Chief Financial Officer", "department": "Finance",
             "hire_date": date(2016, 6, 15), "salary": 275000, "manager_id": 1},
            {"employee_id": "EMP004", "first_name": "David", "last_name": "Kim",
             "email": "david.kim@company.com", "phone": "+1-555-0104",
             "title": "Chief People Officer", "department": "Human Resources",
             "hire_date": date(2017, 2, 1), "salary": 250000, "manager_id": 1},
            
            # VPs (report to C-Suite)
            {"employee_id": "EMP005", "first_name": "Jennifer", "last_name": "Williams",
             "email": "jennifer.williams@company.com", "phone": "+1-555-0105",
             "title": "VP of Engineering", "department": "Technology",
             "hire_date": date(2017, 8, 15), "salary": 220000, "manager_id": 2},
            {"employee_id": "EMP006", "first_name": "Robert", "last_name": "Taylor",
             "email": "robert.taylor@company.com", "phone": "+1-555-0106",
             "title": "VP of Product", "department": "Product",
             "hire_date": date(2018, 1, 10), "salary": 210000, "manager_id": 2},
            {"employee_id": "EMP007", "first_name": "Amanda", "last_name": "Brown",
             "email": "amanda.brown@company.com", "phone": "+1-555-0107",
             "title": "VP of Finance", "department": "Finance",
             "hire_date": date(2018, 4, 1), "salary": 200000, "manager_id": 3},
            
            # Directors/Managers
            {"employee_id": "EMP008", "first_name": "James", "last_name": "Wilson",
             "email": "james.wilson@company.com", "phone": "+1-555-0108",
             "title": "Engineering Manager", "department": "Technology",
             "hire_date": date(2019, 2, 15), "salary": 180000, "manager_id": 5},
            {"employee_id": "EMP009", "first_name": "Lisa", "last_name": "Anderson",
             "email": "lisa.anderson@company.com", "phone": "+1-555-0109",
             "title": "Engineering Manager", "department": "Technology",
             "hire_date": date(2019, 5, 1), "salary": 175000, "manager_id": 5},
            {"employee_id": "EMP010", "first_name": "Christopher", "last_name": "Martinez",
             "email": "christopher.martinez@company.com", "phone": "+1-555-0110",
             "title": "Product Manager", "department": "Product",
             "hire_date": date(2019, 8, 20), "salary": 165000, "manager_id": 6},
            {"employee_id": "EMP011", "first_name": "Michelle", "last_name": "Garcia",
             "email": "michelle.garcia@company.com", "phone": "+1-555-0111",
             "title": "HR Manager", "department": "Human Resources",
             "hire_date": date(2019, 11, 1), "salary": 120000, "manager_id": 4},
            
            # Senior Engineers
            {"employee_id": "EMP012", "first_name": "Daniel", "last_name": "Lee",
             "email": "daniel.lee@company.com", "phone": "+1-555-0112",
             "title": "Senior Software Engineer", "department": "Technology",
             "hire_date": date(2020, 3, 15), "salary": 160000, "manager_id": 8},
            {"employee_id": "EMP013", "first_name": "Jessica", "last_name": "Thompson",
             "email": "jessica.thompson@company.com", "phone": "+1-555-0113",
             "title": "Senior Software Engineer", "department": "Technology",
             "hire_date": date(2020, 5, 1), "salary": 155000, "manager_id": 8},
            {"employee_id": "EMP014", "first_name": "Matthew", "last_name": "White",
             "email": "matthew.white@company.com", "phone": "+1-555-0114",
             "title": "Senior Software Engineer", "department": "Technology",
             "hire_date": date(2020, 7, 20), "salary": 150000, "manager_id": 9},
            {"employee_id": "EMP015", "first_name": "Ashley", "last_name": "Harris",
             "email": "ashley.harris@company.com", "phone": "+1-555-0115",
             "title": "Senior Software Engineer", "department": "Technology",
             "hire_date": date(2020, 9, 1), "salary": 155000, "manager_id": 9},
            
            # Junior Engineers
            {"employee_id": "EMP016", "first_name": "Kevin", "last_name": "Clark",
             "email": "kevin.clark@company.com", "phone": "+1-555-0116",
             "title": "Software Engineer", "department": "Technology",
             "hire_date": date(2021, 1, 10), "salary": 110000, "manager_id": 8},
            {"employee_id": "EMP017", "first_name": "Stephanie", "last_name": "Lewis",
             "email": "stephanie.lewis@company.com", "phone": "+1-555-0117",
             "title": "Software Engineer", "department": "Technology",
             "hire_date": date(2021, 4, 15), "salary": 105000, "manager_id": 8},
            {"employee_id": "EMP018", "first_name": "Brian", "last_name": "Robinson",
             "email": "brian.robinson@company.com", "phone": "+1-555-0118",
             "title": "Software Engineer", "department": "Technology",
             "hire_date": date(2021, 7, 1), "salary": 100000, "manager_id": 9},
            {"employee_id": "EMP019", "first_name": "Nicole", "last_name": "Walker",
             "email": "nicole.walker@company.com", "phone": "+1-555-0119",
             "title": "Junior Software Engineer", "department": "Technology",
             "hire_date": date(2022, 2, 1), "salary": 85000, "manager_id": 9},
            
            # Other departments
            {"employee_id": "EMP020", "first_name": "Andrew", "last_name": "Hall",
             "email": "andrew.hall@company.com", "phone": "+1-555-0120",
             "title": "Financial Analyst", "department": "Finance",
             "hire_date": date(2021, 3, 1), "salary": 95000, "manager_id": 7},
            {"employee_id": "EMP021", "first_name": "Rachel", "last_name": "Young",
             "email": "rachel.young@company.com", "phone": "+1-555-0121",
             "title": "HR Specialist", "department": "Human Resources",
             "hire_date": date(2021, 6, 15), "salary": 75000, "manager_id": 11},
            {"employee_id": "EMP022", "first_name": "Thomas", "last_name": "King",
             "email": "thomas.king@company.com", "phone": "+1-555-0122",
             "title": "Product Designer", "department": "Product",
             "hire_date": date(2021, 9, 1), "salary": 130000, "manager_id": 10},
            {"employee_id": "EMP023", "first_name": "Laura", "last_name": "Scott",
             "email": "laura.scott@company.com", "phone": "+1-555-0123",
             "title": "UX Researcher", "department": "Product",
             "hire_date": date(2022, 1, 10), "salary": 115000, "manager_id": 10},
            {"employee_id": "EMP024", "first_name": "Ryan", "last_name": "Green",
             "email": "ryan.green@company.com", "phone": "+1-555-0124",
             "title": "DevOps Engineer", "department": "Technology",
             "hire_date": date(2022, 4, 1), "salary": 140000, "manager_id": 5},
            {"employee_id": "EMP025", "first_name": "Megan", "last_name": "Adams",
             "email": "megan.adams@company.com", "phone": "+1-555-0125",
             "title": "Accountant", "department": "Finance",
             "hire_date": date(2022, 6, 15), "salary": 80000, "manager_id": 7},
        ]
        
        # Create employees
        for emp_data in employees_data:
            employee = Employee(
                employee_id=emp_data["employee_id"],
                first_name=emp_data["first_name"],
                last_name=emp_data["last_name"],
                email=emp_data["email"],
                phone=emp_data["phone"],
                title=emp_data["title"],
                department=emp_data["department"],
                hire_date=emp_data["hire_date"],
                salary=emp_data["salary"],
                status=EmployeeStatus.ACTIVE,
                manager_id=emp_data["manager_id"]
            )
            db.add(employee)
        
        db.commit()
        print(f"Created {len(employees_data)} employees")
        
        # Create teams
        teams_data = [
            {"name": "Executive Team", "description": "Company leadership and executives", "lead_id": 1},
            {"name": "Engineering", "description": "Software development and infrastructure", "lead_id": 5},
            {"name": "Backend Team", "description": "Backend services and APIs", "lead_id": 8, "parent_team_id": 2},
            {"name": "Frontend Team", "description": "User interfaces and web applications", "lead_id": 9, "parent_team_id": 2},
            {"name": "Product", "description": "Product management and design", "lead_id": 6},
            {"name": "Finance", "description": "Financial operations and accounting", "lead_id": 7},
            {"name": "Human Resources", "description": "People operations and culture", "lead_id": 11},
        ]
        
        for team_data in teams_data:
            team = Team(
                name=team_data["name"],
                description=team_data["description"],
                lead_id=team_data["lead_id"],
                parent_team_id=team_data.get("parent_team_id")
            )
            db.add(team)
        
        db.commit()
        print(f"Created {len(teams_data)} teams")
        
        # Add team members
        team_members = [
            # Executive Team
            (1, [1, 2, 3, 4]),
            # Engineering
            (2, [2, 5, 8, 9, 24]),
            # Backend Team
            (3, [8, 12, 13, 16, 17]),
            # Frontend Team
            (4, [9, 14, 15, 18, 19]),
            # Product
            (5, [6, 10, 22, 23]),
            # Finance
            (6, [3, 7, 20, 25]),
            # HR
            (7, [4, 11, 21]),
        ]
        
        for team_id, employee_ids in team_members:
            for emp_id in employee_ids:
                member = TeamMember(team_id=team_id, employee_id=emp_id)
                db.add(member)
        
        db.commit()
        print("Added team members")
        
        print("Database seeded successfully!")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

