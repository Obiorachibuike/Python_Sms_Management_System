import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import User, SMSSent  # Import your SQLAlchemy models

# Create GraphQL types for each SQLAlchemy model
class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User  # Link to the User model

class SMSSentType(SQLAlchemyObjectType):
    class Meta:
        model = SMSSent  # Link to the SMSSent model

# Define your queries
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)  # Query for all users
    all_sms_sent = graphene.List(SMSSentType)  # Query for all SMS sent records

    def resolve_all_users(self, info):
        return User.query.all()  # Fetch all users from the database

    def resolve_all_sms_sent(self, info):
        return SMSSent.query.all()  # Fetch all SMS sent records from the database

# Create the GraphQL schema
schema = graphene.Schema(query=Query)
