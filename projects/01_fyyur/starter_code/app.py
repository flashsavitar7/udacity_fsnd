#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime
from distutils.log import error
from http.client import responses
import dateutil.parser
import babel
import sys
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, raiseExceptions
from sqlalchemy import desc
from flask_wtf import Form
from forms import *
from models import db, Venue, Show, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venue_list = Venue.query.distinct(Venue.city, Venue.state).order_by(desc(Venue.city)).all()
  for venue in venue_list:
    city_and_state = {"city": venue.city, "state": venue.state}
    
    venues = Venue.query.filter_by(city = venue.city, state = venue.state).all()
    
    result = []
    for venue in venues:
      result.append({
        "id": venue.id,
        "name": venue.name
      })
      
    city_and_state["venues"] = result
    data.append(city_and_state)
    
  return render_template('pages/venues.html', areas=data)
    

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '')
  search = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data = []

  for result in search:
    data.append({
      "id": result.id,
      "name": result.name,
      
    })
  
  response={
    "count": len(search),
    "data": data
  }
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)

    past = []
    upcoming = []

    for show in venue.shows:
        temp = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past.append(temp)
        else:
            upcoming.append(temp)

    data=vars(venue)
    data['past_shows'] = past
    data['upcoming_shows'] = upcoming
    data['past_shows_num'] = len(past)
    data['upcoming_shows_num'] = len(upcoming)
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertio
      try:
        form = VenueForm(request.form)
        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      genres=form.genres.data, 
                      facebook_link=form.facebook_link.data,
                      seeking_description=form.seeking_description.data,
                      website_link=form.website_link.data,
                      seeking_talent=form.seeking_talent.data
                      
                      )
        
        
        # commit session to database
        db.session.add(venue)
        db.session.commit()

        # flash success 
      except:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # catches errors
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        # closes session
      finally:
        db.session.close()
        return render_template('pages/home.html')
        
  
  

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  if request.method == 'GET':
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was deleted successfully')
    
  else:
    db.session.rollback
    flash('Failed attenpt to delete venue')
    db.session.close()
  
  return redirect(url_for('venues', venue_id=venue_id))
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term', '')
  search = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  data = []

  for result in search:
    data.append({
      "id": result.id,
      "name": result.name,
      
    })
  
  response={
    "count": len(search),
    "data": data
  }
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    past = []
    upcoming = []

    for show in artist.shows:
        temp = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past.append(temp)
        else:
            upcoming.append(temp)

    data=vars(artist)
    data['past_shows'] = past
    data['upcoming_shows'] = upcoming
    data['past_shows_num'] = len(past)
    data['upcoming_shows_num'] = len(upcoming)
    
    
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  
  
  
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if request.method == 'POST':
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.facebook_link=form.facebook_link.data
    artist.image_link=form.image_link.data
    artist.seeking_venue=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
    artist.website_link=form.website_link.data

    # Add the updated data and commit
    db.session.add(artist)
    db.session.commit()
    flash("Artist " + artist.name + " was successfully edited!")
  else:
    db.session.rollback()
    print(sys.exc_info())
    flash("Sorry," + artist.name + " failed to be edited.")
  
  
  return redirect(url_for('show_artist', artist_id=artist_id))


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if request.method == 'POST':
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.phone=form.phone.data
    venue.genres=form.genres.data
    venue.facebook_link=form.facebook_link.data
    venue.image_link=form.image_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    venue.website_link=form.website_link.data

    # Add and commit the new updates
    db.session.add(venue)
    db.session.commit()
    flash("Venue " + venue.name + " was successfully edited")
  else:
    db.session.rollback()
    print(sys.exc_info())
    flash("Sorry, Venue failed to be edited.")
    
    
  
  return redirect(url_for('show_venue', venue_id=venue_id))

# TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
   
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertio
      try:
        form = ArtistForm(request.form)
        artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.city.data,
                        phone=form.phone.data,
                        genres=form.genres.data, 
                        image_link=form.image_link.data, 
                        facebook_link=form.facebook_link.data
                        
                        )
        
        db.session.add(artist)
        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
        db.session.close()

      return render_template('pages/home.html')
        
    
  # called upon submitting 
  # the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #status=done


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows_query = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in shows_query: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
      form = ShowForm(request.form)
      show = Show(
                  artist_id = form.artist_id.data,
                  venue_id = form.venue_id.data,
                  start_time = form.start_time.data
                )
      
      db.session.add(show)
      db.session.commit()

      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')
  
  
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''