from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = (engine)

DBsession = sessionmaker(bind=engine)
session = DBsession()


class webServerHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    try:
      if self.path.endswith("/restaurants/new"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        output = ""
        output += "<html><body>"
        output += "<h1>Make a New Restaurant</h1>"
        output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
        output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
        output += "<input type='submit' value='Create'>"
        output += "</form></body></html>"

        #output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
        #output += "<input name='newRestaurantName' type='text' placeholder='New Restaurant Name'>"
        #output += "<input type='submit' value='Create'>"
        #output += "</form>"
        #output += "</body></html>"

        self.wfile.write(output)
        return

      if self.path.endswith("/delete"):
        IDPath = self.path.split("/")[2]
        result = session.query(Restaurant).filter_by(id=IDPath).one()

        if result:
          self.send_response(200)
          self.send_header('Content-type', 'text/html')
          self.end_headers()

          output = ""
          output += "<html><body>"
          output += "<h1>Are you sure you want to delete %s?</h1>" % result.name

          output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % IDPath
          output += "<input type='submit' value='Delete'>"
          output += "</form>"
          output += "</html></body>"
          self.wfile.write(output)


      if self.path.endswith("/edit"):
        IDPath = self.path.split("/")[2]
        result = session.query(Restaurant).filter_by(id=IDPath).one()

        if result:
          self.send_response(200)
          self.send_header('Content-type', 'text/html')
          self.end_headers()

          output = ""
          output += "<html><body>"

          output += "<h1>" + result.name + "</h1>"

          output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % IDPath
          output += "<input name='newRestaurantName' type='text' placeholder='%s'>" % result.name
          output += "<input type='submit' value='Rename'>"
          output += "</form>"

          output += "</html></body>"

          self.wfile.write(output)




      if self.path.endswith("/restaurants"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        output += "<html><body>"
        output += "<a href='/restaurants/new'>Make a New Restaurant Here</a>"
        output += '<br><br>'

        all_restaurants = session.query(Restaurant).all()
        for res in all_restaurants:
          output += res.name + '\n'
          output += '<br>'
          output += "<a href='/restaurants/%s/edit'>Edit</a>" % res.id
          output += '<br>'
          output += "<a href='/restaurants/%s/delete'>Remove</a>" % res.id
          output += '<br>'
          output += '<br>'

        output += "</body></html>"

        self.wfile.write(output)
        print output
        return

    except IOError:
      self.send_error(404, 'File Not Found: %s' % self.path)

  def do_POST(self):
    try:
      if self.path.endswith("/delete"):
        IDPath = self.path.split("/")[2]
        result = session.query(Restaurant).filter_by(id=IDPath).one()

        if result:
          session.delete(result)
          session.commit()
          self.send_response(301)
          self.send_header('Content-type', 'text/html')
          self.send_header('Location', '/restaurants')
          self.end_headers()

      if self.path.endswith("/edit"):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if ctype == 'multipart/form-data':
          fields = cgi.parse_multipart(self.rfile, pdict)
          messagecontent = fields.get('newRestaurantName')
          IDPath = self.path.split("/")[2]

          result = session.query(Restaurant).filter_by(id=IDPath).one()

          if result:
            result.name = messagecontent[0]
            session.add(result)
            session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()


      if self.path.endswith("/restaurants/new"):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        if ctype == 'multipart/form-data':
          fields = cgi.parse_multipart(self.rfile, pdict)

          messagecontent = fields.get('newRestaurantName')

          newRestaurant = Restaurant(name=messagecontent[0])
          session.add(newRestaurant)
          session.commit()

          self.send_response(301)
          self.send_header('Content-type', 'text/html')
          self.send_header('Location', '/restaurants')
          self.end_headers()

          return




      # self.send_response(301)
      # self.send_header('Content-type', 'text/html')
      # self.end_headers()

      # ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

      # if ctype == 'multipart/form-data':
      #   fields = cgi.parse_multipart(self.rfile, pdict)
      #   messagecontent = fields.get('message')

      #   output = ''

      #   self.wfile.write(output)
      #   print output
    except:
      pass

def main():
  try:
    port = 8080
    server = HTTPServer(('', port), webServerHandler)
    print "Web Server running on port %s" % port
    server.serve_forever()
  except:
    print " ^C entered, stopping web server...."
    server.socket.close()

if __name__ == '__main__':
  main()
