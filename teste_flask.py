from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    # Process the incoming webhook data
    data = request.json  # Assuming JSON data
    print("Received webhook data:", data)

    # You can add logic here to:
    # - Validate the data (e.g., check for required fields, verify signatures)
    # - Perform actions based on the data (e.g., update a database, send notifications)

    return "ok"


if __name__ == '__main__':
    app.run(debug=True, port=5000)