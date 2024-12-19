from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from sqlalchemy import exc

#flask - web framework for py that allows creation of web apps. 
app = Flask(__name__) 

#app.config - dictionary to set config variables for flask app 
#SQLALCHEMY_DATABASE_URI tells flask where db is located
#sqlite is type of db. database.db is name of db. /// means db is on local file system
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#SQLALchemy is an ORM that allows us to interact with database using python objects
#sqlalchemy(app) binds the flask app to the sqlalchemy instance (db) 
db = SQLAlchemy(app)

api = Api(app)

#modeling our data (object)
# a class is a blueprint for creating objects
#db.Model: This means that UserModel inherits from db.Model, which is SQLAlchemy's base class for database models. It tells SQLAlchemy that this class corresponds to a table in the database.
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(80), unique=True, nullable=True)

    def __repr__(self):
        return f"User(name = {self.name}, email={self.email})"
    

#define arguments that are gona come in with reqparse
#used for validating data when sending data to api 
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="email cannot be blank")

#how we want the data to look in json
userFields = {
    'id': fields.Integer, 
    'name': fields.String,
    'email': fields.String,
}

#create an endpoint using Resource class 
class Users(Resource):
    #GET handler for Users resource
    @marshal_with(userFields) 
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user)
        try:
            db.session.commit()  # Commit the session to save changes
        except exc.IntegrityError:  # Catch the unique constraint violation
            db.session.rollback()  # Rollback the session to maintain integrity
            return {"message": "A database integrity error occurred"}, 400
        
        users = UserModel.query.all()
        #201 http status is created 
        return users, 201 

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message='user not found')
        return user
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="user not found")
        user.name=args["name"]
        user.email=args["email"]
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="user not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users
 
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/')
def home():
    return '<h1>FLASK REST API</h1>'

if __name__ == "__main__":
    app.run (debug=True)



