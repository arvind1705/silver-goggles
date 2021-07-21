# silver-goggles
    
## Steps to run assignment locally:

1. Navigate to the silver-goggles folder : `cd silver-goggles/`
2. Run the docker compose with API_KEY param: `API_KEY="<your_youtube_access_token>" docker-compose up --build`
    
Visit http://0.0.0.0:8000/swagger/ in your browser to access swagger UI.


Incase API Key is not available remove API_KEY param and run as below.
    
    docker-compose up --build

Visit http://0.0.0.0:8000/api/mock_data in your browser to insert mock data into DB.



