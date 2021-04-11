import json
import random
import string
from typing import Dict

from app import db, jwt
from werkzeug.security import check_password_hash, generate_password_hash


class Client(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    mail_to = db.Column(db.Text, nullable=True)
    webhook_url = db.Column(db.Text, nullable=True)
    xss = db.relationship("XSS", backref="client", lazy="dynamic")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def get_dashboard_stats(self):

        number_of_captured_data = 0
        xss = XSS.query.filter_by(client_id=self.id).all()
        for hit in xss:
            number_of_captured_data += len(json.loads(hit.data))
        return {
            "owner_id": self.owner_id,
            "id": self.id,
            "name": self.name,
            "reflected": XSS.query.filter_by(client_id=self.id).filter_by(xss_type="reflected").count(),
            "stored": XSS.query.filter_by(client_id=self.id).filter_by(xss_type="stored").count(),
            "data": number_of_captured_data,
        }

    def get_dict_representation(self):

        if self.owner_id:
            owner = User.query.filter_by(id=self.owner_id).first().username
        else:
            owner = "Nobody"
        return {"owner": owner, "id": self.id, "name": self.name, "description": self.description, "mail_to": self.mail_to, "webhook_url": self.webhook_url}

    def generate_uid(self):

        characters = string.ascii_letters + string.digits
        new_uid = "".join(random.choice(characters) for _ in range(6))

        while Client.query.filter_by(uid=new_uid).first():
            new_uid = "".join(random.choice(characters) for _ in range(6))

        self.uid = new_uid


class XSS(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    headers = db.Column(db.Text, server_default="{}", nullable=False)
    ip_addr = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, server_default="{}", nullable=False)
    tags = db.Column(db.Text, server_default="[]", nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    xss_type = db.Column(db.Text, nullable=False)

    def get_dict_representation(self):

        data = {
            "id": self.id,
            "headers": json.loads(self.headers),
            "ip_addr": self.ip_addr,
            "data": json.loads(self.data),
            "timestamp": self.timestamp,
            "tags": json.loads(self.tags),
        }
        if "fingerprint" in data["data"].keys():
            data["data"]["fingerprint"] = ""
        if "dom" in data["data"].keys():
            data["data"]["dom"] = ""
        if "screenshot" in data["data"].keys():
            data["data"]["screenshot"] = ""

        return data

    def get_summary(self):

        return {"id": self.id, "ip_addr": self.ip_addr, "timestamp": self.timestamp, "tags": json.loads(self.tags)}


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_login = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    client = db.relationship("Client", backref="owner", lazy="dynamic")

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):

        return check_password_hash(self.password_hash, password)

    def generate_password(self):

        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(12))

    def get_dict_representation(self):

        return {"id": self.id, "username": self.username, "first_login": self.first_login, "is_admin": self.is_admin}


class Settings(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    smtp_host = db.Column(db.Text, nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    smtp_mail_from = db.Column(db.Text, nullable=True)
    smtp_mail_to = db.Column(db.Text, nullable=True)
    smtp_user = db.Column(db.Text, nullable=True)
    smtp_pass = db.Column(db.Text, nullable=True)
    smtp_ssl_tls = db.Column(db.Boolean, default=False, nullable=True)
    smtp_starttls = db.Column(db.Boolean, default=False, nullable=True)
    webhook_url = db.Column(db.Text, nullable=True)

    def get_dict_representation(self):

        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_starttls": self.smtp_starttls,
            "smtp_ssl_tls": self.smtp_ssl_tls,
            "smtp_mail_from": self.smtp_mail_from,
            "smtp_mail_to": self.smtp_mail_to,
            "smtp_user": self.smtp_user,
            "webhook_url": self.webhook_url,
        }


class Blocklist(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.Text, nullable=False, unique=True)


@jwt.user_lookup_loader
def user_loader_callback(jwt_header: Dict, jwt_payload: Dict) -> User:

    return User.query.filter_by(username=jwt_payload["sub"]).first()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header: Dict, jwt_payload: Dict) -> bool:

    if jwt_payload["type"] == "access":
        return False
    else:
        blocked_jti = Blocklist.query.filter_by(jti=jwt_payload["jti"]).first()
        return bool(blocked_jti)


def init_app(app):

    with app.app_context():
        if db.session.query(User).count() != 0:
            print("[-] User creation not needed")
        else:
            user = User(username="admin", is_admin=1)
            user.set_password("xss")
            db.session.add(user)
            db.session.commit()
            print("[+] Initial user created")

        if db.session.query(Settings).count() != 0:
            print("[-] Settings initialization not needed")
        else:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print("[+] Settings initialization successful")
        if db.session.query(Blocklist).count() == 0:
            print("[-] JWT blocklist reset not needed")
        else:
            db.session.query(Blocklist).delete()
            db.session.commit()
            print("[+] JWT blocklist reset successful")
