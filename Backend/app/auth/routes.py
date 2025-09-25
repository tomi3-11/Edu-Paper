from flask_restful import Resource, Api
from flask import Blueprint, request
from app.forms import RegistrationForm
from app.models import User
from app import db, csrf
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/Api')

api = Api(auth_bp)

csrf.exempt(auth_bp)


class RegistrationResource(Resource): 
    def post(self):
        data = request.get_json()
        form = RegistrationForm(data=data)
        
        if not form.validate():
            print(form.errors)
            return form.errors, 400
        
        # Checking for existing email or username
        if User.query.filter_by(username=form.username.data).first():
            return {
                "message": "Username already exists"
            }, 409
        
        if User.query.filter_by(email=form.email.data).first():
            return {
                "message": "Email already exists"
            }, 409
            
        new_user = User(
            username=form.username.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)
        
        db.session.add(new_user)
        db.session.commit()
        
        return {
            "message": "User registered successfully"
        }, 201
        
    
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        print("📩 Incoming data:", data)  # Debugging
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {
                "message": "email or password required"
            }, 400
            
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            additional_claims = {"role": user.role}
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            ) # Create a JWT
            return {
                "message": "Login In successfully", "access_token": access_token
            }, 200
        else:
            return {
                "message": "Invalid email or password."
            }, 401
            
        
api.add_resource(RegistrationResource, '/register')
api.add_resource(LoginResource, '/login')
