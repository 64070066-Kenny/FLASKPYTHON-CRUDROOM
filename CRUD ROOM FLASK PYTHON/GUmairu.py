from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS



client = MongoClient("mongodb://localhost:27017")
db = client["SOA"]
collection = db["BookingRoom"]
collection1 = db["ROOM"]

app = Flask(__name__)
CORS(app)

@app.route("/purpose")
def requestpur():
    pur = []
    for x in collection.find():
        x['_id'] = str(x['_id'])
        
        pur.append(x['purpose'])
        print(x)
    return jsonify({'purposed': pur})

@app.route("/GetRoom")
def getRoom():
    # Your existing code...

    rooms = []
    for room in collection1.find():
        rooms.append(room['room_name'])

    response = jsonify({'room_name': rooms})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    
    return response

@app.route("/GetAllRoom")
def getAllRoom():
    rooms = []
    for room in collection1.find():
        room_data = {
            'room_id': str(room['_id']),
            'room_name': room['room_name'],
            'room_description': room['room_description'],
            'room_participants': room['room_participants'],
        }
        rooms.append(room_data)

    response = jsonify({'rooms': rooms})
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

@app.route("/getById/<string:id>")
def getById(id):
    for x in collection.find():
        x['_id'] = str(x['_id'])
        if x['_id'] == id:
            return jsonify({'room': x})


@app.route("/detailpurpose/<string:id>")
def detail(id):
    print(id)
    box = []
    for x in collection.find():
        x['_id'] = str(x['_id'])
        if x['_id'] == id:
            box.append(x)
            print(x)
    return jsonify({'detail': box})

@app.route("/aprrovestatus/<string:id>", methods=["GET"])
def modifystatus(id):
    # Convert the 'id' parameter to a valid ObjectId
    id_obj = ObjectId(id)

    # Check if a document with the provided '_id' exists
    existing_document = collection.find_one({'_id': id_obj})

    if existing_document:
        # Update the status to 'Approve'
        result = collection.update_one({'_id': id_obj}, {'$set': {'status': 'Approve'}})

        # Fetch the updated document
        updated_document = collection.find_one({'_id': id_obj})

        # Convert ObjectId to string for JSON serialization
        updated_document['_id'] = str(updated_document['_id'])

        return jsonify({'new': updated_document})

    return jsonify({'message': 'Document not found'}, 404)

@app.route("/rejectstatus/<string:id>", methods=["GET"])
def Rejectstatus(id):
    # Convert the 'id' parameter to a valid ObjectId
    id_obj = ObjectId(id)

    # Check if a document with the provided '_id' exists
    existing_document = collection.find_one({'_id': id_obj})

    if existing_document:
        # Update the status to 'Not Approve'
        result = collection.update_one({'_id': id_obj}, {'$set': {'status': 'Not Approve'}})

        # Fetch the updated document
        updated_document = collection.find_one({'_id': id_obj})

        # Convert ObjectId to string for JSON serialization
        updated_document['_id'] = str(updated_document['_id'])

        return jsonify({'new': updated_document})

    return jsonify({'message': 'Document not found'}, 404)

@app.route("/create", methods=["POST"])
def createRoom():
    # Access form data from the request
    room_name = request.form.get("room_name")
    room_description = request.form.get("room_description")
    room_participants = request.form.get("room_participants")

    if room_name and room_description and room_participants:
        # Check if a room with the same name already exists
        existing_room = collection1.find_one({"room_name": room_name})

        if existing_room:
            # Return an error message if the room name is already taken
            return {"message": f"Room name '{room_name}' is already taken. Choose a different name."}, 400

        # Create a new document and insert it into collection1
        new_room = {
            "room_name": room_name,
            "room_description": room_description,
            "room_participants": room_participants
        }

        collection1.insert_one(new_room)

        # Return a success message
        return {"message": "Room created successfully"}
    else:
        # Return an error message if required data is missing
        return {"message": "Missing room_name, room_description, or room_participants in the form data"}, 400

@app.route("/update/<string:id>", methods=["POST"])
def updateRoom(id):
    # Access form data from the request
    updated_roomName = request.form.get("room_name")
    updated_description = request.form.get("room_description")
    updated_participants = request.form.get("room_participants")

    if updated_roomName and updated_description and updated_participants:
        # Convert the 'id' parameter to a valid ObjectId
        id_obj = ObjectId(id)

        # Find the existing document with the specified _id
        existing_room = collection1.find_one({"_id": id_obj})

        if existing_room:
            # Check if the updated room name already exists (excluding the document being updated)
            duplicate_room = collection1.find_one({"room_name": updated_roomName, "_id": {"$ne": id_obj}})

            if duplicate_room:
                # Return an error message if the updated room name is already taken
                return {"message": f"Room name '{updated_roomName}' is already taken. Choose a different name."}, 400

            # Update the fields in collection1
            collection1.update_one(
                {"_id": id_obj},
                {"$set": {"room_name": updated_roomName, "room_description": updated_description, "room_participants": updated_participants}}
            )

            # Update the room name in BookingRoom collection
            collection.update_many(
                {"roomName": existing_room["room_name"]},
                {"$set": {"roomName": updated_roomName}}
            )

            # Return a success message
            return {"message": f"Room {id} updated successfully"}
        else:
            # Return an error message if the document is not found
            return {"message": f"Room with id {id} not found"}, 404
    else:
        # Return an error message if required data is missing
        return {"message": "Missing room_description or room_participants in the form data"}, 400

@app.route("/delete/<string:id>", methods=["DELETE"])
def deleteRoom(id):
    # Convert the 'id' parameter to a valid ObjectId
    id_obj = ObjectId(id)

    # Find the existing document with the specified _id
    existing_room = collection1.find_one({"_id": id_obj})

    if existing_room:
        # Check if the room name is present in the BookingRoom collection
        room_in_booking = collection.find_one({"roomName": existing_room["room_name"]})

        if room_in_booking:
            return jsonify({"message": f"Room {existing_room['room_name']} is booked and cannot be deleted"}), 400

        # Delete the document with the specified _id
        result = collection1.delete_one({"_id": id_obj})

        # Check if the document was successfully deleted
        if result.deleted_count > 0:
            return {"message": f"Room {id} deleted successfully"}
        else:
            return {"message": "Failed to delete room"}, 500  # Internal Server Error
    else:
        return {"message": f"Room with id {id} not found"}, 404

if __name__ == "__main__":
    app.run(port=5001)
    

