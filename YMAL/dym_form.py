import re
import secrets
from pathlib import Path

import yaml
from flask import Response, abort, render_template, request, session

SOURCE = Path(__file__).with_name("exmple.yaml")
NAME = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
IMAGE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._/@:-]{0,254}")
FIELDS = ("name", "namespace", "replicas", "container_name", "image", "port")


def load_example():
    with SOURCE.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if data.get("apiVersion") != "apps/v1" or data.get("kind") != "Deployment":
        raise ValueError("Unsupported example kind")
    return data


def current_values(data):
    container = data["spec"]["template"]["spec"]["containers"][0]
    return {
        "name": data["metadata"]["name"],
        "namespace": data["metadata"]["namespace"],
        "replicas": data["spec"]["replicas"],
        "container_name": container["name"],
        "image": container["image"],
        "port": container["ports"][0]["containerPort"],
    }


def apply_values(data, fields):
    for name in ("name", "namespace", "container_name"):
        if not NAME.fullmatch(fields[name]):
            raise ValueError("Invalid Kubernetes name")
    if not IMAGE.fullmatch(fields["image"]):
        raise ValueError("Invalid image reference")
    for name in ("replicas", "port"):
        if not re.fullmatch(r"[0-9]{1,5}", fields[name]):
            raise ValueError("Expected an integer")
    replicas, port = int(fields["replicas"]), int(fields["port"])
    if not 0 <= replicas <= 100 or not 1 <= port <= 65535:
        raise ValueError("Integer outside allowed range")
    data["metadata"].update(name=fields["name"], namespace=fields["namespace"])
    data["spec"]["replicas"] = replicas
    container = data["spec"]["template"]["spec"]["containers"][0]
    container.update(name=fields["container_name"], image=fields["image"])
    container["ports"][0]["containerPort"] = port
    return data


def form_view():
    data = load_example()
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        if not secrets.compare_digest(token, session["csrf_token"]):
            abort(403)
        expected = set(FIELDS) | {"csrf_token"}
        if set(request.form) != expected or any(len(request.form.getlist(k)) != 1 for k in expected):
            abort(400)
        try:
            data = apply_values(data, request.form)
        except ValueError:
            abort(400, "Invalid manifest field")
        return Response(
            yaml.safe_dump(data, sort_keys=False),
            mimetype="application/yaml",
            headers={"Content-Disposition": 'attachment; filename="deployment.yaml"',
                     "X-Content-Type-Options": "nosniff"},
        )
    return render_template("editor.html", values=current_values(data),
                           csrf_token=session["csrf_token"])
