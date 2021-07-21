# silver-goggles

## Installation
  
    $ git clone https://github.com/arvind1705/silver-goggles.git
    $ cd silver-goggles
    $ API_KEY="<your_youtube_access_token>" docker-compose up --build # Make sure docker and docker compose is installed.
    
Visit http://0.0.0.0:8000/swagger/ in your browser to access swagger UI.


Incase API Key is not available remove API_KEY param and run as below.
    
    $ docker-compose up --build

Visit http://0.0.0.0:8000/api/mock_data in your browser to insert mock data into DB.



