import os
from dotenv import load_dotenv                           
from fastapi import FastAPI 
import psycopg2

  #since you can't push the connection string in github, we make an env file and add our database_URL there then a gitignore file=> everything mentioned in this will be ignored even if u ask github to push everything [env, pycache]
 #then we install python-dotenv => import os, load_dotenv=> this guy will read our db_url from env file
load_dotenv()
app = FastAPI()
db_url=os.getenv("database_URL")

# try to connect but if doesn't work it doesn't die there, jab home pe knock hoga to app.get("/") will return that its connected or not

try:
    connection= psycopg2.connect(db_url)
except Exception as e:
    connection = None
    print(f"Pantry is locked! Error: {e}")

@app.get("/")
def home():
    return {"message": "Chef is in the kitchen"}


# {
#pehle saari lights show kr rhe the but ab bas nearby region ki krenge isliye commented this one
# 2. A new doorbell specifically to see the lights
# @app.get("/lights")
# def get_lights():
#     if connection is None:
#         return {"error": "Pantry is currently locked. Check your network!"}
#     # 3. Use the Tray (Cursor) inside the function
#     cursor = connection.cursor()
#     #cursor.execute("SELECT name FROM street_light")
#     cursor.execute("SELECT name, ST_AsText(location) FROM street_light")
#     all_lights = cursor.fetchall() # Fetches everything on the tray
#     cursor.close()  
#     return {"street_light": all_lights}
#  }


#STORY:
#nearby function jab call hoga to get_nearby_lights func will run with lat,lon parameters and if there's no connection to it will return else cursor apni tray and query ka letter leke jayega => query{ name and text mae convert krke location select kro from street light table WHERE jo location ho vo within 500m ho , meter mae rakhne ke liye ::geometry use kra hai }
#ab cursor execute hoga and neon database mae se required tuples banake return kr dega jo results mae store honge, return krke json file mae web pe show kr denge

@app.get("/nearby")
def get_nearby_lights(lat: float, lon: float):
    if connection is None:
        return {"error":"empty pantry"}
    
    cursor=connection.cursor()

    query= """
    SELECT name, ST_AsText(location)
    FROM street_light
    WHERE ST_DWithin(
    location::geometry,
    ST_SetSRID(ST_MakePoint(%s,%s),4326)::geometry,
    500
    );
    """

    cursor.execute(query,(lon,lat))
    results=cursor.fetchall()
    cursor.close()

    # return {
    #     "user location": {"lat": lat, "lon": lon},
    #     "nearby_lights": results,
    #     "count": len(results)
    # }

#This was working fine but it would give all the tuples in same line, to make it look better we will take an empty clean_result array and start by taking one tupple at a time and divide it into name, lat, lon: name is simply the first element in the tuple but lat and lon are like Point(lat,lon) so we will first delete this Point word and then split at the gap to get both

    clean_result=[]
    for row in results:
        name=row[0]
        raw_cord=row[1]
        cord=raw_cord.replace("POINT(","").replace(")","").split(" ")
        light_object={
            "name": name,
            "lon":float(cord[0]),
            "lat":float(cord[1])
        }
        clean_result.append(light_object)

    count=len(clean_result)
    return {
        "counts":count,
        "lights": clean_result,
        "status":"Its dark" if count==0 else "Its Safe"
    }






                             