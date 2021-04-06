from app import db
from app.api.endpoints import bp
from app.api.utils.shared import generate_message_response
from app.api.utils.x import generate_xss_properties, send_alert
from app.models import XSS, Client
from flask import request
from flask_cors import cross_origin


@bp.route("/x/<xss_type>/<uid>", methods=["GET", "POST"])
@cross_origin()
def catch_xss(xss_type, uid):

    client = Client.query.filter_by(uid=uid).first()

    if not client:
        return generate_message_response("OK")

    xss = XSS(**generate_xss_properties(request, xss_type, client))

    db.session.add(xss)
    db.session.commit()

    send_alert(xss)

    return generate_message_response("OK")
