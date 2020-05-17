from flask import jsonify, request
from app import db
from app.models import Client, XSS, User
from app.api import bp
from flask_login import login_required, current_user
from app.validators import not_empty, check_length

import json


@bp.route('/client', methods=['PUT'])
@login_required
def create_client():
    data = request.form

    if 'name' not in data.keys() or\
       'description' not in data.keys():
        return jsonify({'status': 'error', 'detail': 'Missing name or description'}), 400

    if Client.query.filter_by(name=data['name']).first() != None:
        return jsonify({'status': 'error', 'detail': 'Client already exists'}), 400

    if not_empty(data['name']) and check_length(data['name'], 32) and check_length(data['description'], 128):

        new_client = Client(
            name=data['name'], description=data['description'], owner_id=current_user.id)

        new_client.gen_uid()

        db.session.add(new_client)

        db.session.commit()
        return jsonify({'status': 'OK'}), 201
    else:
        return jsonify({'status': 'error', 'detail': 'Invalid data (name empty or too long or description too long)'}), 400


@bp.route('/client/<id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def get_client(id):

    if request.method == 'GET':

        client = Client.query.filter_by(id=id).first_or_404()

        return jsonify(client.to_dict_client()), 200

    elif request.method == 'POST':

        data = request.form

        client = Client.query.filter_by(id=id).first_or_404()

        if current_user.id != client.owner_id and not current_user.is_admin:
            return jsonify({'status': 'error', 'detail': 'Can\'t modify someone else\'s client'}), 403

        if 'name' in data.keys():

            if client.name != data['name']:
                if Client.query.filter_by(name=data['name']).first() != None:
                    return jsonify({'status': 'error', 'detail': 'Another client already uses this name'}), 400

            if not_empty(data['name']) and check_length(data['name'], 32):
                client.name = data['name']
            else:
                return jsonify({'status': 'error', 'detail': 'Invalid name (too long or empty)'}), 400

        if 'description' in data.keys():

            if check_length(data['description'], 128):
                client.description = data['description']
            else:
                return jsonify({'status': 'error', 'detail': 'Invalid description (too long)'}), 400

        if 'owner' in data.keys():
            if not current_user.is_admin:
                return jsonify({'status': 'error', 'detail': 'Only an admin can do that'}), 403
            user = User.query.filter_by(id=data['owner']).first()
            if user == None:
                return jsonify({'status': 'error', 'detail': 'This user does not exist'}), 400
            client.owner_id = data['owner']

        db.session.commit()

        return jsonify({'status': 'OK'}), 200

    elif request.method == 'DELETE':

        client = Client.query.filter_by(id=id).first_or_404()

        if current_user.id != client.owner_id and not current_user.is_admin:
            return jsonify({'status': 'error', 'detail': 'Can\'t delete someone else\'s client'}), 403

        XSS.query.filter_by(client_id=id).delete()

        db.session.delete(client)
        db.session.commit()

        return jsonify({'status': 'OK'}), 200


@bp.route('/client/<id>/<flavor>', methods=['GET'])
@login_required
def get_client_xss_list(id, flavor):

    if flavor != 'reflected' and flavor != 'stored':
        return jsonify({'status': 'error', 'detail': 'Unknown XSS type'}), 400

    xss_list = []
    xss = XSS.query.filter_by(client_id=id).filter_by(xss_type=flavor).all()

    for hit in xss:
        xss_list.append(hit.to_dict_short())

    return jsonify(xss_list), 200


@bp.route('/client/<id>/<flavor>/<xss_id>', methods=['GET'])
@login_required
def get_client_xss(id, flavor, xss_id):

    if flavor != 'reflected' and flavor != 'stored':
        return jsonify({'status': 'error', 'detail': 'Unknown XSS type'}), 400

    xss = XSS.query.filter_by(client_id=id).filter_by(
        xss_type=flavor).filter_by(id=xss_id).first_or_404()

    return jsonify(xss.to_dict()), 200


@bp.route('/client/<id>/loot', methods=['GET'])
@login_required
def get_client_loot(id):

    loot = {}

    xss = XSS.query.filter_by(client_id=id).all()

    for hit in xss:
        for element in json.loads(hit.data).items():
            if element[0] not in loot.keys():
                loot[element[0]] = []
            elif element[0] == 'fingerprint':
                loot[element[0]].append({hit.id: json.loads(element[1])})
            else:
                loot[element[0]].append({hit.id: element[1]})

    return jsonify(loot), 200
