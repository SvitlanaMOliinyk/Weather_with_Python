from flask import Blueprint, redirect

hello_bp = Blueprint('hello', __name__)

@hello_bp.route('/')
def hello():
    return redirect('/weather')