from flask import Flask
import os


raw_names = os.listdir("./figures")
name_list = [name.replace(".png", "") for name in raw_names]
print(name_list)

# app = Flask(__name__)
#
#
# @app.route("/")
# def home():
#     return "sup ho"
#
#
# if __name__ == "__main__":
#     app.run(debug=True)
