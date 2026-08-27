"""
Farook Ajose — Portfolio
Flask app: server-side rendering for public pages, backed by Supabase Postgres.
Admin auth + writes happen entirely client-side (see admin_login.html /
add-project.html) — this file never touches write operations.
"""

import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, render_template, abort
from flask_bootstrap import Bootstrap5
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.config["SUPABASE_URL"] = os.environ["SUPABASE_URL"]
app.config["SUPABASE_ANON_KEY"] = os.environ["SUPABASE_ANON_KEY"]

bootstrap = Bootstrap5(app)

# Server-side Supabase client, used only for public reads (Home/Projects/detail
# pages). Uses the same anon key as the browser — RLS already permits public
# SELECT on the projects table, so no service-role key is needed here.
supabase: Client = create_client(
    app.config["SUPABASE_URL"], app.config["SUPABASE_ANON_KEY"]
)


@app.context_processor
def inject_year():
    return {"current_year": date.today().year}


@app.route("/")
def home():
    response = (
        supabase.table("projects")
        .select("*")
        .eq("featured", True)
        .order("date", desc=True)
        .limit(3)
        .execute()
    )
    return render_template("index.html", featured_projects=response.data)


@app.route("/projects")
def projects():
    response = supabase.table("projects").select("*").order("date", desc=True).execute()
    return render_template("project.html", projects=response.data)


@app.route("/projects/<slug>")
def project_detail(slug):
    response = (
        supabase.table("projects").select("*").eq("slug", slug).limit(1).execute()
    )
    if not response.data:
        abort(404)
    project = response.data[0]

    # "Next" follows the same order as the Projects grid (most recent
    # first), so the next older project is fetched — the row with the
    # closest earlier date.
    next_response = (
        supabase.table("projects")
        .select("*")
        .lt("date", project["date"])
        .order("date", desc=True)
        .limit(1)
        .execute()
    )

    if next_response.data:
        next_project = next_response.data[0]
    else:
        # Reached the oldest project — wrap around to the newest one
        # so the link never dead-ends.
        wrap_response = (
            supabase.table("projects")
            .select("*")
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        next_project = wrap_response.data[0] if wrap_response.data else None
        # Guard against a single-project catalog linking to itself.
        if next_project and next_project["slug"] == project["slug"]:
            next_project = None

    return render_template(
        "project-detail.html", project=project, next_project=next_project
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/admin")
def admin_login():
    return render_template("admin-login.html")


@app.route("/admin/add-project")
def add_project():
    return render_template("add-project.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
