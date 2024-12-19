from api import app, db

#in flask we have to give it app_context so it knows which app we are trying to work with 
#the code in the block can interact with the app (Access db connection, request handler, etc)

with app.app_context():
    db.create_all() #this method creates all the database tables
    #it reads all classes that inherit from db.Model