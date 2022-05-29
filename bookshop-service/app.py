"""
    Bookshop service

    Features:
    - Map Visualisation
    - Poster Generator
    - Minting NFTs 
    - Book Recommender
"""

from flask import Flask, redirect, url_for, render_template, request, flash, session
# from flask.ext.session import Session
import requests 
import folium
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'


"""
    Contains all constants used in the app
"""

NODE_API_PORT = 3000
FOLIUM_DEFAULT_LOCATION = [42.3601, -71.0589]
FLASK_PORT = 5000

"""
Loading up objects for book recommendation
"""
with open("../book-recommender/book_df.pkl", "rb") as f:
    df = pickle.load(f)

with open("../book-recommender/sentence_embeddings.pkl", "rb") as f:
    embeddings = pickle.load(f)

with open("../book-recommender/model.pkl", "rb") as f:
    model = pickle.load(f)




"""
    Base Route
        - Return Homepage
"""
@app.route("/")
def home():
    return render_template(url_for("home"))

"""
    Add Coordinate Route
        - Form filling
        - Flash message on successful addition of form item
"""
@app.route("/addmapelement", methods = ["GET","POST"])
def add_map():
    if request.method == 'POST':
        # Get the form elements
        lat = request.form["latitude"]
        lon = request.form["longitude"]
        addr = request.form["address"]
        name = request.body["name"]
        description = request.body["description"]
        
        # If the item added is a bookshop
        if request.form.get("bookshop"):
            special = "1"
        else:
            special = "0"

        # API Call
        endpoint = f"http://127.0.0.1:5000/{NODE_API_PORT}/addlocation/"
        data = {
            "lat" : lat, 
            "lon" : lon,
            "addr" : addr,
            "name" : name,
            "desc" : description,
            "special" : special
        }

        r = requests.post(endpoint, data)

        # Successful API Call
        if str(r.status_code) == "200":
            flash("Item added successfully")
            return redirect(url_for("add_map"))

        # Unsuccessful API Call
        else:
            flash("There was an error adding this item.")
            return redirect(url_for("home"))

    else:
        return render_template(url_for("add_map"))


"""
    View All Points Route
        - JSON Parsing
        - Different Map Icons
"""
@app.route("/maps")
def maps():
    # API Call
    endpoint = f"http://127.0.0.1:5000/{NODE_API_PORT}/getlocations/"
    
    r = requests.post(endpoint)

    # Unsuccessful API Call
    if str(r.status_code) != "200":
        flash("There was an error getting all locations")
        return redirect(url_for("home"))

    # Successful API Call
    else:
        # Parsing the JSON Response
        data = r.json()

        # Default Tooltips
        book_store_tooltip = "Book Store"
        other_item_tooltip = "Cool Place"

        # Initialising the map
        m = folium.Map(location = FOLIUM_DEFAULT_LOCATION, zoom_start=12)

        # Default icons
        book_store_icon = folium.Icon(color='yellow',icon='leaf')
        other_item_icon = folium.Icon(color='blue',icon='leaf')

        # Adding the folium markers
        for item in data:
            latitude = item[1]
            longitude = item[2]
            address = item[3]
            name = item[4]
            desc =  item[5]
            special = item[6]

            location = []
            location.append(latitude)
            location.append(longitude)

            popup_string = f"Check out <strong> {name} </strong> at {address}. {desc}"

            # Special marker for bookstore
            if str(special) == "1":
                folium.Marker(location, popup= popup_string,tooltip = book_store_tooltip, icon=book_store_icon).add_to(m)
            else:
                folium.Marker(location, popup= popup_string,tooltip = other_item_tooltip, icon=other_item_icon).add_to(m)

            # Saving the map data
            m.save("templates/map.html")
            flash("Locations loaded successfully, hover over them to see more details.")
            return render_template("map.html")

"""
    Create new NFT Route
        - Upload to IPFS
        - File Upload
"""        
@app.route("/nft", methods = ["GET", "POST"])
def nft():
    if request.method == 'POST':
        # Get the form elements
        file_name = request.form["file_name"]
        uploaded_file = request.files['file']
        
        # API Call
        endpoint = f"http://127.0.0.1:5000/{NODE_API_PORT}/upload"
        data = {
            "file" : uploaded_file, 
            "file_name" : file_name,
        }

        r = requests.post(endpoint, data)

        # Successful API Call
        if str(r.status_code) == "200":
            flash("NFT generated successfully")
            return render_template(url_for("nft"), file_loc = r.json())

        # Unsuccessful API Call
        else:
            flash("There was an error generating the IPFS location.")
            return redirect(url_for("home"))

    else:
        return render_template(url_for("nft"), file_loc = None)



"""
    Book Recommendation Route
        - Sentence Embeddings
        - Dataset
"""
@app.route("/book", methods = ["GET", "POST"])
def book():
    if request.method == 'POST':
        # Get Book Summary
        summary = request.form["summary"]

        # Encode the given sentence
        new_embedding = model.encode(summary)

        # Get recommendations
        similarity_score = cosine_similarity(new_embedding, embeddings).flatten()
        recommended_list = sorted(list(enumerate(similarity_score)),reverse=True,key=lambda x:x[1])[0:5]

        books_list = []
        for i in recommended_list:
            books_list.append(df.iloc[i[0]].BookTitle)


        return render_template(url_for("book"), rec_list = recommended_list)
    
    else:
        return render_template(url_for("book"), rec_list = None)

"""
    Poster Designer
"""
@app.route("/design")
def design():
    return render_template(url_for("design"))







