from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cacao.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.String, nullable=False)
    climate = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    reason_price = db.Column(db.String, nullable=True)
    problems = db.Column(db.String, nullable=True)
    other_observations = db.Column(db.String, nullable=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    quantity = float(request.form["quantity"])
    date = request.form["date"]
    price = float(request.form["price"])

    # Climat
    climate = request.form.get("climate_select")
    if climate == "autre":
        climate = request.form.get("climate_other")

    # Raisons du prix (multi-choix)
    reason_price_list = request.form.getlist("reason_price")
    reason_price = ", ".join(reason_price_list)
    if "autre" in reason_price_list:
        reason_price += " (" + request.form.get("reason_price_other") + ")"

    # Problèmes rencontrés (multi-choix)
    problems_list = request.form.getlist("problems")
    problems = ", ".join(problems_list)

    other_observations = request.form["other_observations"]

    new_production = Production(
        quantity=quantity,
        date=date,
        climate=climate,
        price=price,
        reason_price=reason_price,
        problems=problems,
        other_observations=other_observations,
    )
    db.session.add(new_production)
    db.session.commit()

    flash("Données enregistrées avec succès !")
    return redirect(url_for("index"))


@app.route("/visualize")
def visualize():
    productions = Production.query.all()
    if productions:
        climates = list(set([prod.climate for prod in productions]))
        climate_map = {c: i for i, c in enumerate(climates)}

        X = np.array([climate_map[prod.climate] for prod in productions])
        y = np.array([prod.quantity for prod in productions])

        graph_path = os.path.join("static", "production_climate.png")

        # Vérification avant régression
        if len(np.unique(X)) > 1 and len(np.unique(y)) > 1:
            try:
                coeffs = np.polyfit(X, y, 1)
                trend = np.poly1d(coeffs)

                plt.figure(figsize=(8, 5))
                plt.scatter(X, y, color="#8B4513", label="Données réelles")
                plt.plot(X, trend(X), color="#27ae60", label="Régression linéaire")
                plt.xticks(ticks=range(len(climates)), labels=climates, rotation=30)
                plt.title("Production de cacao en fonction du climat")
                plt.xlabel("Climat")
                plt.ylabel("Production (tonnes)")
                plt.legend()
                plt.tight_layout()
                plt.savefig(graph_path)
                plt.close()
            except np.linalg.LinAlgError:
                # Si la régression échoue, on affiche juste les points
                plt.figure(figsize=(8, 5))
                plt.scatter(X, y, color="#8B4513", label="Données réelles")
                plt.xticks(ticks=range(len(climates)), labels=climates, rotation=30)
                plt.title("Production de cacao en fonction du climat")
                plt.xlabel("Climat")
                plt.ylabel("Production (tonnes)")
                plt.legend()
                plt.tight_layout()
                plt.savefig(graph_path)
                plt.close()
        else:
            # Trop peu de diversité → juste scatter
            plt.figure(figsize=(8, 5))
            plt.scatter(X, y, color="#8B4513", label="Données réelles")
            plt.xticks(ticks=range(len(climates)), labels=climates, rotation=30)
            plt.title("Production de cacao en fonction du climat")
            plt.xlabel("Climat")
            plt.ylabel("Production (tonnes)")
            plt.legend()
            plt.tight_layout()
            plt.savefig(graph_path)
            plt.close()
    else:
        graph_path = None

    return render_template(
        "visualize.html", graph_path=graph_path, productions=productions
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
