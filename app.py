from flask import Flask, render_template, request, jsonify
import json
import os
import uuid

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"categories": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories')
def get_categories():
    data = load_data()
    return jsonify(list(data['categories'].keys()))

@app.route('/api/cards/<category>')
def get_cards(category):
    data = load_data()
    if category in data['categories']:
        return jsonify(data['categories'][category]['cards'])
    return jsonify([])

@app.route('/api/cards', methods=['POST'])
def add_card():
    data = load_data()
    req = request.json
    category = req.get('category')
    front = req.get('front')
    back = req.get('back')
    if not category or front is None or back is None:
        return jsonify({'error': 'Missing fields'}), 400
    if category not in data['categories']:
        data['categories'][category] = {'cards': []}
    card = {
        'id': str(uuid.uuid4()),
        'front': front,
        'back': back
    }
    data['categories'][category]['cards'].append(card)
    save_data(data)
    return jsonify(card), 201

@app.route('/api/cards/<card_id>', methods=['PUT'])
def update_card(card_id):
    data = load_data()
    req = request.json
    front = req.get('front')
    back = req.get('back')
    new_category = req.get('category')
    for cat, content in data['categories'].items():
        for idx, card in enumerate(content['cards']):
            if card['id'] == card_id:
                if front is not None:
                    card['front'] = front
                if back is not None:
                    card['back'] = back
                if new_category and new_category != cat:
                    content['cards'].pop(idx)
                    if new_category not in data['categories']:
                        data['categories'][new_category] = {'cards': []}
                    data['categories'][new_category]['cards'].append(card)
                save_data(data)
                return jsonify(card)
    return jsonify({'error': 'Card not found'}), 404

@app.route('/api/cards/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    data = load_data()
    for cat, content in data['categories'].items():
        for idx, card in enumerate(content['cards']):
            if card['id'] == card_id:
                content['cards'].pop(idx)
                save_data(data)
                return jsonify({'message': 'deleted'})
    return jsonify({'error': 'Card not found'}), 404

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = load_data()
    req = request.json
    category = req.get('category')
    if not category:
        return jsonify({'error': 'Missing category name'}), 400
    if category in data['categories']:
        return jsonify({'error': 'Category already exists'}), 400
    data['categories'][category] = {'cards': []}
    save_data(data)
    return jsonify({'message': 'created'}), 201

@app.route('/api/categories/<category>', methods=['DELETE'])
def delete_category(category):
    data = load_data()
    if category in data['categories']:
        del data['categories'][category]
        save_data(data)
        return jsonify({'message': 'deleted'})
    return jsonify({'error': 'Category not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
