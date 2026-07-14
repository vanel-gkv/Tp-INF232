from flask import Flask, render_template, Response
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Bienvenue sur mon service Render !"


@app.route("/visualize")
def visualize():
    # Exemple de graphique simple
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30], marker="o")
    ax.set_title("Exemple de visualisation")

    # Sauvegarde dans un buffer mémoire
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Conversion en base64 pour affichage dans HTML
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    # Retourne une page HTML avec l’image
    html = f"""
    <html>
        <body>
            <h1>Visualisation</h1>
            <img src="data:image/png;base64,{img_base64}" />
        </body>
    </html>
    """
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

