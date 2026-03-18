import os
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

# .env file load karna
load_dotenv()

app = Flask(__name__)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.hisab_pro_db
locations_collection = db.locations
entries_collection = db.entries

# 1. Frontend Serve karna
@app.route('/')
def index():
    return render_template('index.html')

# 2. Locations API
@app.route('/api/locations', methods=['GET', 'POST'])
def handle_locations():
    if request.method == 'POST':
        data = request.json
        new_loc = {"name": data['name']}
        result = locations_collection.insert_one(new_loc)
        return jsonify({"id": str(result.inserted_id), "name": data['name']}), 201
    
    locations = []
    for loc in locations_collection.find():
        locations.append({"id": str(loc['_id']), "name": loc['name']})
    return jsonify(locations)

@app.route('/api/locations/<loc_id>', methods=['DELETE'])
def delete_location(loc_id):
    locations_collection.delete_one({"_id": ObjectId(loc_id)})
    # Us location ki saari entries bhi delete kardo
    entries_collection.delete_many({"loc_id": loc_id})
    return jsonify({"success": True})

# 3. Entries API
@app.route('/api/entries/<loc_id>', methods=['GET', 'POST'])
def handle_entries(loc_id):
    if request.method == 'POST':
        data = request.json
        new_entry = {
            "loc_id": loc_id,
            "category": data['category'],
            "details": data['details'],
            "amount": data['amount'],
            "date": data['date']
        }
        result = entries_collection.insert_one(new_entry)
        new_entry['id'] = str(result.inserted_id)
        del new_entry['_id']
        return jsonify(new_entry), 201
    
    entries = []
    for ent in entries_collection.find({"loc_id": loc_id}):
        entries.append({
            "id": str(ent['_id']),
            "category": ent['category'],
            "details": ent['details'],
            "amount": ent['amount'],
            "date": ent['date']
        })
    return jsonify(entries)

@app.route('/api/entries/delete/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entries_collection.delete_one({"_id": ObjectId(entry_id)})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
