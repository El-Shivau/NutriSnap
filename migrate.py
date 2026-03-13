import os
from sqlalchemy import create_engine, MetaData
engine = create_engine('postgresql://postgres:NutriSnap4664@db.cnlfyelbfvcxlwaqbtin.supabase.co:5432/postgres')
from app import app, db
with app.app_context(): db.create_all()
