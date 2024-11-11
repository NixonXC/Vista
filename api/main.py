from flask import Flask, request, redirect, url_for, render_template
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests

app = Flask(__name__)

@app.route('/')
def movies():
    return render_template('index.html')

@app.route('/series')
def series():
    return render_template('series.html')


url = "https://imdb8.p.rapidapi.com/title/find"

headers = {
	"x-rapidapi-key": "f96c60ec5emsh4b6451611214d81p14212fjsn9c2839c99d87",
	"x-rapidapi-host": "imdb8.p.rapidapi.com"
}

def getInfo(id):
    url = f"https://www.myapifilms.com/imdb/idIMDB?idIMDB={id}&token=c236aee8-d43d-4646-bc9f-edac76062307"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Access the first movie from the 'movies' array
    return data["data"]["movies"][0]  # Adjusted to access the first movie object

# Create a route for my contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send', methods=['POST','GET'])
def send():
    url = "https://discord.com/api/webhooks/1092031417577373817/P9Mkxczmjxi2NgMY1-lBQ00PdVbPTyw7v6kA7u5igM7RCnhonlNufa6hsb-NLAoKXMBP"
    webhook = DiscordWebhook(url=url)
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    embed = DiscordEmbed(title=f"Name: {name}", description='Message From Vista', color='03b2f8')
    embed.add_embed_field(name="Email", value=email, inline=False)
    embed.add_embed_field(name="Message", value=message)
    webhook.add_embed(embed)
    webhook.execute()
    return redirect("/contact")


@app.route('/movie')
def movie():
    x = request.args.get('name')
    querystring = {"q":f"{x}"}
    
    # Get the movie ID by title search
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()["results"][0]
    id = data["id"].split("/")[2]
    # Fetch detailed information using the ID
    meta = getInfo(id)
    
    # Extract relevant data from meta
    date = meta.get("year", "N/A")     
    plot = meta.get("simplePlot", "No plot available.")
    rating = meta.get("rating", "No rating.")
    genre = ', '.join(meta.get("genres", [])) 
    
    vidsrc = f"https://vidsrc.xyz/embed/movie?imdb={id}&ds_lang=en"

    return render_template('movieplayer.html', 
                           movie=data["title"], 
                           year=date, 
                           plot=plot, 
                           rating=rating, 
                           genre=genre,
                           vid = vidsrc
                           )

@app.route('/watch')
def watch():
    x = request.args.get('name')
    y = request.args.get('epi')
    z = request.args.get('season')
    querystring = {"q":f"{x}"}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    id = data["results"][0]["id"].split("/")[2]
    secondary = requests.get('https://imdb8.p.rapidapi.com/title/get-seasons', headers=headers, params={"tconst":id})
    data_2 = secondary.json()
    episode_title = data_2[int(z) - 1]["episodes"][int(y) - 1]["title"]
    epid = data_2[int(z) - 1]["episodes"][int(y) - 1]["id"].split("/")[2]
    tertiary = requests.get('https://imdb8.p.rapidapi.com/title/get-plots', headers=headers, params={"tconst": epid})
    plot = tertiary.json()["plots"][0]["text"]
    print(plot)
    meta = getInfo(id)
    
    date = meta.get("year", "N/A")     
    rating = meta.get("rating", "No rating.")
    genre = ', '.join(meta.get("genres", [])) 
    
    vidsrc = f"https://vidsrc.xyz/embed/tv?imdb={id}&season={z}&episode={y}"

    return render_template('seriesplayer.html', 
                           movie=x + " | " + episode_title, 
                           season=z,
                            episode=y,
                           year=date, 
                           plot=plot, 
                           rating=rating, 
                           genre=genre,
                           vid = vidsrc
                           )


if __name__ == '__main__':
    app.run(debug=True)
