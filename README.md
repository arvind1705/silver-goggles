# Backend Assignment | FamPay
    
## Steps to run assignment locally:

1. Make sure Docker and docker-compose is installed.
2. Clone git repository. `git clone https://github.com/arvind1705/silver-goggles.git`
3. Navigate to the silver-goggles folder : `cd silver-goggles/`
4. Run the docker compose with API_KEY param: `API_KEY="<your_youtube_access_token>" docker-compose up --build`


Visit http://0.0.0.0:8000/ in your browser to access table.
    
Visit http://0.0.0.0:8000/swagger/ in your browser to access swagger UI to view API documentation.

Incase API Key is not available remove API_KEY param and run as below.
    
    docker-compose up --build

Visit http://0.0.0.0:8000/api/mock_data in your browser to insert mock data into DB.

