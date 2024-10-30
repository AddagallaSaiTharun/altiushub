from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import json 
import datetime
import os

cur_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(cur_dir, "Invoice.db")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

number = [1]

def gen_uuid():
    return str(uuid.uuid4())

class InvoiceHeader(db.Model):
    _tablename_="invoice_header"
    id = db.Column(db.String, primary_key=True,default=gen_uuid)
    date = db.Column(db.DateTime, nullable=False,default=datetime.datetime.now)
    invoice_number = db.Column(db.Integer,default = number[0],nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    billing_address = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.String(50), nullable=False)
    GSTIN = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)

class InvoiceItem(db.Model):
    _tablename_="invoice_item"
    invoice_id = db.Column(db.String, db.ForeignKey('invoice_header.id'), nullable=False)
    id = db.Column(db.String, primary_key=True,default=gen_uuid)
    item_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

class InvoiceBillSundry(db.Model):
    _tablename_="invoice_bill_sundry"
    id = db.Column(db.String, primary_key=True,default=gen_uuid)
    invoice_id = db.Column(db.String, db.ForeignKey('invoice_header.id'), nullable=False)
    bill_sundry_name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

# db.create_all()

@app.route('/invoice',methods=["GET","POST","PUT","DELETE"])
def invoice_handler():
    if request.method == 'GET':
        data = request.get_json()
        if data:
            invoice = InvoiceHeader.query.filter(InvoiceHeader.id == data["id"]).first()
            invoice_items = InvoiceItem.query.filter(InvoiceItem.invoice_id == data["id"]).all()
            invoice_bill_sundries = InvoiceBillSundry.query.filter(InvoiceBillSundry.invoice_id == data["id"]).all()
            return jsonify({
                    "invoice":{"id":invoice.id,"date":invoice.date,"invoice_number":invoice.invoice_number,"customer_name":invoice.customer_name,"billing_address":invoice.billing_address,"shipping_address":invoice.shipping_address,"GSTIN":invoice.GSTIN,"total_amount":invoice.total_amount},
                    "invoice_items":{"id":[item.id for item in invoice_items], "item_name":[item.item_name for item in invoice_items], "quantity":[item.quantity for item in invoice_items], "price":[item.price for item in invoice_items], "amount":[item.amount for item in invoice_items]},
                    "invoice_bill_sundries":{"id":[sundry.id for sundry in invoice_bill_sundries], "bill_sundry_name":[sundry.bill_sundry_name for sundry in invoice_bill_sundries], "amount":[sundry.amount for sundry in invoice_bill_sundries]}
                }),200
        message = {"message":[]}
        invoices = InvoiceHeader.query.all()
        for invoice in invoices:
            invoice_items = InvoiceItem.query.filter(InvoiceItem.invoice_id == invoice.id).all()
            invoice_bill_sundries = InvoiceBillSundry.query.filter(InvoiceBillSundry.invoice_id == invoice.id).all()
            message["message"].append(
                {
                    "invoice":{"id":invoice.id,"date":invoice.date,"invoice_number":invoice.invoice_number,"customer_name":invoice.customer_name,"billing_address":invoice.billing_address,"shipping_address":invoice.shipping_address,"GSTIN":invoice.GSTIN,"total_amount":invoice.total_amount},
                    "invoice_items":{"id":[item.id for item in invoice_items], "item_name":[item.item_name for item in invoice_items], "quantity":[item.quantity for item in invoice_items], "price":[item.price for item in invoice_items], "amount":[item.amount for item in invoice_items]},
                    "invoice_bill_sundries":{"id":[sundry.id for sundry in invoice_bill_sundries], "bill_sundry_name":[sundry.bill_sundry_name for sundry in invoice_bill_sundries], "amount":[sundry.amount for sundry in invoice_bill_sundries]}
                }
            )
        return jsonify(message)
    
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({"error":"No data provided"}),400
        
        totalamount=0
        for item in data["invoice_items"]:
            totalamount+=item["amount"]
        for sundry in data["invoice_bill_sundries"]:
            totalamount+=sundry["amount"]

        if data["total_amount"]!=totalamount:
            return jsonify({"error":"Total amount is not correct"}),400
        
        invoice = InvoiceHeader(customer_name=data["customer_name"],billing_address=data["billing_address"],shipping_address=data["shipping_address"],GSTIN=data["GSTIN"],total_amount=data["total_amount"],invoice_number=number[0])
        number[0]+=1
        db.session.add(invoice)
        db.session.commit()
        invoice_items = data["invoice_items"]
        for item in invoice_items:
            if item["amount"]<=0 :
                return jsonify({"error":"Amount for "+data["invoice_items"]["item_name"] +"cannot be negative or zero"}),400
            if item["price"]<=0 :
                return jsonify({"error":"price for "+data["invoice_items"]["item_name"] +"cannot be negative or zero"}),400
            if item["quantity"]<=0 :
                return jsonify({"error":"quantity for "+data["invoice_items"]["item_name"] +"cannot be negative or zero"}),400
            if item["quantity"] * item["price"] != item["amount"]:
                return jsonify({"error":"Amount for "+data["invoice_items"]["item_name"] +"cannot be negative or zero"}),400
            invoice_item = InvoiceItem(invoice_id=invoice.id,item_name=item["item_name"],quantity=item["quantity"],price=item["price"],amount=item["amount"])
            db.session.add(invoice_item)
            db.session.commit()
            
        invoice_bill_sundries = data["invoice_bill_sundries"]
        for sundry in invoice_bill_sundries:
            invoice_bill_sundry = InvoiceBillSundry(invoice_id=invoice.id,bill_sundry_name=sundry["name"],amount=sundry["amount"])
            db.session.add(invoice_bill_sundry)
        
        db.session.commit()
        return jsonify({"message":"Invoice with "+ invoice.customer_name + " has been added"}),200
    
    if request.method == 'PUT':
        data = request.get_json()
        if data["action"] == "invoice":
            invoice = InvoiceHeader.query.filter(InvoiceHeader.id == data["id"]).first()
            if not invoice:
                return jsonify({"error":"Invoice with "+ data["id"] +" does not exist"}),400
            if data["date"]:
                invoice.date = data["date"]
            if data["invoice_number"]:
                invoice.invoice_number = data["invoice_number"]
            if data["customer_name"]:
                invoice.customer_name = data["customer_name"]
            if data["billing_address"]:
                invoice.billing_address = data["billing_address"]
            if data["shipping_address"]:
                invoice.shipping_address = data["shipping_address"]
            if data["GSTIN"]:
                invoice.GSTIN = data["GSTIN"]
            return jsonify({ "message":"Invoice with "+ invoice.id + "has been updated"})
        
        if data["action"] == "invoiceItem":
            invoice_item = InvoiceItem.query.filter(InvoiceItem.id == data["id"]).first()
            if not invoice_item:
                return jsonify({"error":"Invoice_item with "+ data["id"] +" does not exist"}),400
            if data["quantity"]:
                invoice_item.quantity = data["quantity"]
            if data["price"]:
                invoice_item.price = data["price"]
            if data["item_name"]:
                invoice_item.item_name = data["item_name"]
            if data["amount"]:
                if data["amount"] != data["price"] * data["quantity"]:
                    return jsonify({"error":"Amount for "+data["item_name"] +" is not correct"}),400
                invoice_item.amount = data["amount"]
            return jsonify({ "message":"Invoice_item with "+ invoice_item.id + "has been updated"})
        
        if data["action"] == "invoiceSundry":
            invoice_sundry = InvoiceBillSundry.query.filter(InvoiceBillSundry.id == data["id"]).first()
            if not invoice_sundry:
                return jsonify({"error":"Invoice_sundry with "+ data["id"] +" does not exist"}),400
            if data["bill_sundry_name"]:
                invoice_sundry.bill_sundry_name = data["bill_sundry_name"]
            if data["price"]:
                invoice_sundry.amount = data["amount"]
            return jsonify({ "message":"Invoice_sundry with "+ invoice_sundry.id + "has been updated"})
        
    if request.method == 'DELETE':
        data = request.get_json()
        if data["action"] == "invoiceItem":
            invoice_item = InvoiceItem.query.filter(InvoiceItem.id == data["id"]).first()
            if not invoice_item:
                return jsonify({"error":"Invoice_item with "+ data["id"] +" does not exist"}),400
            invoice = InvoiceHeader.query.filter(InvoiceHeader.id == invoice_item.invoice_id).first()
            invoice.total_amount -= invoice_item.amount
            invoice_item.delete()
            db.session.commit()
            return jsonify({ "message":"Invoice_item with "+ invoice_item.id + "has been deleted"})
        
        if data["action"] == "invoiceSudry":
            invoice_sundry = InvoiceBillSundry.query.filter(InvoiceBillSundry.id == data["id"]).first()
            if not invoice_sundry:
                return jsonify({"error":"Invoice_sundry with "+ data["id"] +" does not exist"}),400
            invoice = InvoiceHeader.query.filter(InvoiceHeader.id == invoice_sundry.invoice_id).first()
            invoice.total_amount -= invoice_sundry.amount
            invoice_sundry.delete()
            db.session.commit()
            return jsonify({ "message":"Invoice_sundry with "+ invoice_sundry.id + "has been deleted"})
        
        if data["action"] == "invoice":
            invoice = InvoiceHeader.query.filter(InvoiceHeader.id == data["id"]).first()
            if not invoice:
                return jsonify({"error":"Invoice with "+ data["id"] +" does not exist"}),400
            invoice_items = InvoiceItem.query.filter(InvoiceItem.invoice_id == invoice.id).all()
            for item in invoice_items:
                item.delete()
            invoice_bill_sundries = InvoiceBillSundry.query.filter(InvoiceBillSundry.invoice_id == invoice.id).all()
            for sundry in invoice_bill_sundries:
                sundry.delete()
            invoice.delete()
            db.session.commit()
            return jsonify({ "message":"Invoice with "+ invoice.id + "has been deleted"})
        
        return jsonify({"error":"Invalid action"}),400

def main():
    app.run("localhost", debug=True)

if __name__ == "__main__":
    main()        