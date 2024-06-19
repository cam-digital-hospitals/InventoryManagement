# Inventory Management Starter Solution

Run with docker:  
-  `./setup_keys.sh`  
- `docker compose build`  
- `./start.sh`

Navigate to `localhost:8000` in a web browser.  
New items can be set up in the `Stock Management` tab. 

If you need to use the django admin page - for example to edit the unit cost or supplier link of an existing item,   
It can be accessed at `localhost:8000/admin` or is linked from the `Stock Management` tab.  
Log in with:  
- username: `admin`
- password: `shoestring`  
