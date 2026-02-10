from flask import Blueprint, render_template, request, jsonify
from buxxel.database import supabase   # adjust import if supabase client lives elsewhere
from jinja2 import TemplateNotFound

# Define the blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Renders the homepage"""
    return render_template("index.html")


@main_bp.route("/browse")
def browse():
    """Renders the browse page"""
    return render_template("browse.html")
