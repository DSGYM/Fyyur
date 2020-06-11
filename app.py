# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import inspect
import sys
from forms import *
from flask_migrate import Migrate
import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
# db.create_all()
# https://stackoverflow.com/questions/17768940/target-database-is-not-up-to-date => when upgrading does not work?


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(
        db.String(500),
        default="https://upload.wikimedia.org/wikipedia/commons/a/a2/Sydney_Opera_House_Concert_Theatre.JPG",
    )
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return f"<Venue {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    image_link = db.Column(
        db.String(500),
        default="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    )
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return f"<Artist {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship(
        "Artist", backref=db.backref("shows", cascade="all,delete")
    )
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    venue = db.relationship("Venue", backref=db.backref("shows", cascade="all,delete"))


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
# db.create_all()  # Das fliegt raus bei Migrations


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_venues_from_city(data, city):
    venues = []
    subset = [x for x in data if city in x["city"]]
    for item in subset:
        item = {k: item[k] for k in ("id", "name")}
        venues.append(item)
    return venues


def recode_seek(data):
    if data is None:
        return False
    else:
        return True


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = db.session.query(Venue).order_by(Venue.id)
    result = []
    for item in data:
        d = object_as_dict(item)
        result.append(d)

    unique_cities = list(
        {x["city"]: {"city": x["city"], "state": x["state"]} for x in result}.values()
    )

    data = []
    for city in unique_cities:
        cityval = city
        venues = get_venues_from_city(result, city.get("city"))
        cityval.update({"venues": venues})
        data.append(cityval)

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term").lower()

    data = db.session.query(Venue)
    result = []
    for item in data:
        d = object_as_dict(item)
        result.append(d)

    venues = []
    for item in result:
        item = {k: item[k] for k in ("id", "name")}
        venues.append(item)

    subset = [item for item in venues if search_term in item["name"].lower()]

    # response = {
    #     "count": 1,
    #     "data": [{"id": 2, "name": "The Dueling Pianos Bar", "num_upcoming_shows": 0,}],
    # }

    response = {"count": len(subset), "data": subset}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = (
        db.session.query(
            Venue.id,  # 0
            Venue.name,  # 1
            Venue.genres,  # 2
            Venue.address,  # 3
            Venue.city,  # 4
            Venue.state,  # 5
            Venue.phone,  # 6
            Venue.website,  # 7
            Venue.facebook_link,  # 8
            Venue.seeking_talent,  # 9
            Venue.seeking_description,  # 10
            Venue.image_link,  # 11
            Artist.id,  # 12
            Artist.name,  # 13
            Artist.image_link,  # 14
            Show.start_time,  # 15
        )
        .filter(Venue.id == venue_id)
        .outerjoin(Show, Show.venue_id == Venue.id)
        .outerjoin(Artist, Artist.id == Show.artist_id)
    )

    now = datetime.datetime.now()

    shows = []

    for item in data:
        _dict = {
            "artist_id": item[12],
            "artist_name": item[13],
            "artist_image_link": item[14],
            "start_time": item[15],
        }
        shows.append(_dict)

    upcoming_shows = []
    past_shows = []

    for show in shows:
        if show["artist_id"] is not None:
            if show["start_time"] > now:
                show["start_time"] = show["start_time"].strftime("%Y-%m-%dT%H:%M:%S%z")
                upcoming_shows.append(show)
            else:
                show["start_time"] = show["start_time"].strftime("%Y-%m-%dT%H:%M:%S%z")
                past_shows.append(show)

    result = []
    for item in data:
        _dict = {
            "id": item[0],
            "name": item[1],
            "genres": item[2],
            "address": item[3],
            "city": item[4],
            "state": item[5],
            "phone": item[6],
            "website": item[7],
            "facebook_link": item[8],
            "seeking_talent": recode_seek(item[9]),
            "seeking_description": item[10],
            "image_link": item[11],
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
        result.append(_dict)

    result = result[0]

    return render_template("pages/show_venue.html", venue=result)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():

    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    address = request.form["address"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    website = request.form["website"]
    facebook_link = request.form["facebook_link"]
    seeking_talent = request.form.get("seeking_talent")
    seeking_description = request.form["seeking_description"]

    try:
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            website=website,
            facebook_link=facebook_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):

    try:
        venue_to_delete = Venue.query.get(venue_id)
        db.session.delete(venue_to_delete)
        db.session.commit()
        print("delete that crap")
        flash(f"Venue {venue_id } was successfully deleted")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"An error occurred: Venue {venue_id } cound not be deleted")
    finally:
        db.session.close()

    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g.,
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database

    data = db.session.query(Artist).order_by(Artist.id)
    result = []
    for item in data:
        d = object_as_dict(item)
        result.append(d)

    artists = []
    for item in result:
        item = {k: item[k] for k in ("id", "name")}
        artists.append(item)

    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term").lower()

    data = db.session.query(Artist)
    result = []
    for item in data:
        d = object_as_dict(item)
        result.append(d)

    artists = []
    for item in result:
        item = {k: item[k] for k in ("id", "name")}
        artists.append(item)

    subset = [item for item in artists if search_term in item["name"].lower()]

    response = {
        "count": len(subset),
        "data": subset,
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id

    data = (
        db.session.query(
            Artist.id,  # 0
            Artist.name,  # 1
            Artist.genres,  # 2
            Artist.city,  # 3
            Artist.state,  # 4
            Artist.phone,  # 5
            Artist.website,  # 6
            Artist.facebook_link,  # 7
            Artist.seeking_venue,  # 8
            Artist.seeking_description,  # 9
            Artist.image_link,  # 10
            Venue.id,  # 11
            Venue.name,  # 12
            Venue.image_link,  # 13
            Show.start_time,  # 14
        )
        .filter(Artist.id == artist_id)
        .outerjoin(Show, Show.artist_id == Artist.id)
        .outerjoin(Venue, Venue.id == Show.venue_id)
    )

    now = datetime.datetime.now()

    shows = []

    for item in data:
        print(item)

    for item in data:
        _dict = {
            "venue_id": item[11],
            "venue_name": item[12],
            "venue_image_link": item[13],
            "start_time": item[14],
        }
        shows.append(_dict)

    upcoming_shows = []
    past_shows = []

    for show in shows:
        if show["venue_id"] is not None:
            if show["start_time"] > now:
                show["start_time"] = show["start_time"].strftime("%Y-%m-%dT%H:%M:%S%z")
                upcoming_shows.append(show)
            else:
                show["start_time"] = show["start_time"].strftime("%Y-%m-%dT%H:%M:%S%z")
                past_shows.append(show)

    result = []
    for item in data:
        print(item[2])
        _dict = {
            "id": item[0],
            "name": item[1],
            "genres": item[2],
            "city": item[3],
            "state": item[4],
            "phone": item[5],
            "website": item[6],
            "facebook_link": item[7],
            "seeking_venue": recode_seek(item[8]),
            "seeking_description": item[9],
            "image_link": item[10],
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
        result.append(_dict)

    result = result[0]

    return render_template("pages/show_artist.html", artist=result)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):

    form = ArtistForm()

    artist_to_update = Artist.query.filter_by(id=artist_id).one()

    artist = {
        "id": artist_to_update.id,
        "name": artist_to_update.name,
        "genres": artist_to_update.genres,
        "city": artist_to_update.city,
        "state": artist_to_update.state,
        "phone": artist_to_update.phone,
        "website": artist_to_update.website,
        "facebook_link": artist_to_update.facebook_link,
        "seeking_venue": artist_to_update.seeking_venue,
        "seeking_description": artist_to_update.seeking_venue,
        "image_link": artist_to_update.image_link,
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):

    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    facebook_link = request.form["facebook_link"]
    image_link = request.form["image_link"]
    website = request.form["website"]
    seeking_venue = request.form.get("seeking_venue")
    seeking_description = request.form["seeking_description"]

    try:
        artist = Artist.query.filter_by(id=artist_id).one()
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.genres = genres
        artist.facebook_link = facebook_link
        artist.image_link = image_link
        artist.website = website
        artist.seeking_venue = seeking_venue
        artist.seeking_description = seeking_description

        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully updated!")
    except:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be updated."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()

    venue_to_update = Venue.query.filter_by(id=venue_id).one()

    venue = {
        "id": venue_to_update.id,
        "name": venue_to_update.name,
        "genres": venue_to_update.genres,
        "address": venue_to_update.address,
        "city": venue_to_update.city,
        "state": venue_to_update.state,
        "phone": venue_to_update.phone,
        "website": venue_to_update.website,
        "facebook_link": venue_to_update.facebook_link,
        "seeking_talent": venue_to_update.seeking_talent,
        "seeking_description": venue_to_update.seeking_talent,
        "image_link": venue_to_update.image_link,
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):

    name = request.form["name"]
    city = request.form["city"]
    address = request.form["address"]
    state = request.form["state"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    facebook_link = request.form["facebook_link"]
    image_link = request.form["image_link"]
    website = request.form["website"]
    seeking_venue = request.form.get("seeking_venue")
    seeking_description = request.form["seeking_description"]

    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        venue.name = name
        venue.city = city
        venue.address = address
        venue.state = state
        venue.phone = phone
        venue.genres = genres
        venue.facebook_link = facebook_link
        venue.image_link = image_link
        venue.website = website
        venue.seeking_venue = seeking_venue
        venue.seeking_description = seeking_description

        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully updated!")
    except:
        flash(
            "An error occurred. Venue "
            + request.form["name"]
            + " could not be updated."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():

    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]
    phone = request.form["phone"]
    genres = request.form.getlist("genres")
    facebook_link = request.form["facebook_link"]
    image_link = request.form["image_link"]
    website = request.form["website"]
    seeking_venue = request.form.get("seeking_venue")
    seeking_description = request.form["seeking_description"]

    try:
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            image_link=image_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = (
        db.session.query(
            Venue.id,
            Venue.name,
            Artist.id,
            Artist.name,
            Artist.image_link,
            Show.start_time,
        )
        .join(Venue, Venue.id == Show.venue_id)
        .join(Artist, Artist.id == Show.artist_id)
    )

    result = []
    for item in data:
        d = {
            "venue_id": item[0],
            "venue_name": item[1],
            "artist_id": item[2],
            "artist_name": item[3],
            "artist_image_link": item[4],
            "start_time": item[5].strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        result.append(d)

    return render_template("pages/shows.html", shows=result)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    venue_id = request.form["venue_id"]
    artist_id = request.form["artist_id"]
    start_time = request.form["start_time"]

    try:
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except:
        flash(
            "An error occurred. Show on "
            + request.form["start_time"]
            + " could not be listed."
        )
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""

