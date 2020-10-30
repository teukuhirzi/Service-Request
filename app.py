from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#import model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:inthepark@localhost:5432/hirzi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Employee

class Employee(db.Model):
    __tablename__ = 'employee'

    payroll = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String())
    password = db.Column(db.String())
    

    def __init__(self, fullname, password):
        self.fullname = fullname
        self.password = password
       

    def __repr__(self):
        return f"<Employee {self.payroll}>"



@app.route('/')
def hello():
	return {"hello": "world"}


@app.route('/employee', methods=['POST', 'GET'])
def handle_employees():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_employee = Employee(fullname=data['fullname'], password=data['password'])

            db.session.add(new_employee)
            db.session.commit()

            return {"message": f"{new_employee.fullname} adalah pegawai baru."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        employees = Employee.query.all()
        results = [
            {
                "fullname": emp.fullname,
                "password": emp.password
            } for emp in employees]

        return {"count": len(results), "fullname": results, "message": "success"}


@app.route('/employee/<employee_pr>', methods=['GET', 'PUT', 'DELETE'])
def handle_employee(employee_pr):
    emp = Employee.query.get_or_404(employee_pr)

    if request.method == 'GET':
        response = {
            "fullname": emp.fullname
        }
        return {"message": "success", "emp": response}

    elif request.method == 'PUT':
        data = request.get_json()
        emp.fullname = data['fullname']
        emp.password = data['password']

        db.session.add(emp)
        db.session.commit()
        
        return {"message": f"employee {emp.fullname} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(emp)
        db.session.commit()
        
        return {"message": f"Employee {emp.fullname} successfully deleted."}

# Service

class Services(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    tipe = db.Column(db.String())
    unit_price = db.Column(db.Integer())

    def __init__(self, tipe, unit_price):
        self.tipe = tipe
        self.unit_price = unit_price

    def __repr__(self):
        return '<service id {}>'.format(self.id)

    def serialize(self):
        return{
            'id': self.id,
            'tipe': self.tipe,
            'unit_price': self.unit_price
        }   

@app.route('/addService', methods=["POST"])
def add_service():

    body = request.json
    tipe = body['tipe']
    unit_price = body['unit_price']

    try:
        item = Services(
            tipe= tipe,
            unit_price= unit_price
        )

        db.session.add(item)
        db.session.commit()
        return "Service baru ditambahkan, yaitu '{}'".format(item.tipe), 200

    except Exception as e:
        return(str(e)), 400

# ========================================== GET ALL ITEM ================================
@app.route('/getAllServices', methods=["GET"])
def get_all_Services():
        try:
            services = Services.query.all()
            results = [
                {
                    "tipe": srv.tipe,
                    "unit_price": srv.unit_price
                } for srv in services]

            return {"count": len(results), "fullname": results, "message": "success"}
        except Exception as e:
                return (str(e))

# ============================================ GET ITEM BY =====================================
@app.route('/getServiceBy/<itemId_>', methods=["GET"])
def get_service_by(itemId_):
        try:
                item = Services.query.filter_by(id=itemId_).first()
                return jsonify(item.serialize())
        except Exception as e:
                return (str(e))

# =============================================== UPDATE ITEM =====================================
@app.route('/updateService/<itemId_>', methods=["PUT"])
def update_services(itemId_):

        body = request.json
        item_existing = get_service_by(itemId_).json

        if 'tipe' not in body:
                tipe_service = item_existing['tipe']
        else:
                tipe_service = body['tipe']
        if 'unit_price' not in body:
                price_each = item_existing['unit_price']
        else:
                price_each = body['unit_price']
       
        try:
                serviceUpdate = {
                    'tipe': tipe_service,
                    'unit_price': price_each
                }
                item = Services.query.filter_by(id=itemId_).update(serviceUpdate)
                db.session.commit()
                return 'service telah diupdate'
        except Exception as e:
                return(str(e))             

@app.route('/deleteService/<serviceId_>', methods=["DELETE"])  
def delete_service(serviceId_): 
    srv = Services.query.get_or_404(serviceId_)

    db.session.delete(srv)
    db.session.commit()
        
    return {"message": f"Service {srv.tipe} telah dihapus."}






if __name__ == '__main__':
    app.run(debug=True)