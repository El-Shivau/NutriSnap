from repositories.user_repository import UserRepository
from security.auth import generate_token
from werkzeug.security import generate_password_hash, check_password_hash # Using werkzeug as it's already there

class AuthService:
    @staticmethod
    def register(data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'USER')
        
        if UserRepository.get_by_email(email) or UserRepository.get_by_username(username):
             return {'error': 'User already exists'}, 400
             
        password_hash = generate_password_hash(password)
        UserRepository.create(username, email, password_hash, role)
        
        return {'message': 'User created successfully'}, 201

    @staticmethod
    def login(data):
        email = data.get('email')
        password = data.get('password')
        
        user = UserRepository.get_by_email(email)
        
        if not user or not check_password_hash(user.password_hash, password):
            return {'error': 'Invalid credentials'}, 401
            
        token = generate_token(user.id)
        return {'token': token, 'username': user.username, 'role': user.role}, 200
