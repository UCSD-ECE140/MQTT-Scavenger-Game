import json
import time
import random 
import paho.mqtt.client as paho
from paho import mqtt

#------------------------------------------------------
# User login parameteras 
theLogin = "aSender1"
thePassword = "Abcd1234"
theURL = "d5b09983a26545aea3226f271346f52a.s1.eu.hivemq.cloud"

#------------------------------------------------------
# Game Setup

lobby_name = "aLobby1"
team_name = "team2"
player_name = "player3"

# Moves
theMoves = {
    "UP" : (-1, 0),
    "DOWN" : (1, 0),
    "LEFT" : (0, -1),
    "RIGHT" : (0, 1)
}

#------------------------------------------------------
# Definition of response 

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# dispatch the message 
def on_message(client, userdata, msg):
    #print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic_list = msg.topic.split("/")
    # Validate it is input we can deal with
    if topic_list[-1] in dispatch.keys(): 
        dispatch[topic_list[-1]](client, topic_list, msg.payload)

#------------------------------------------------------
# Process Incoming Messages

# Dispatch function: deal with the game state
def game_state(client, topic_list, msg_payload):
    # Get the scores
    aCurentMove = json.loads(msg_payload)
    #Request next move
    anInput = move_request(aCurentMove)
    post_move(client, anInput)
    return

#Dispatch function: deal with the change of the game state
def lobby(client, topic_list, msg_payload):
    if (msg_payload).decode()[:9] == "Game Over":
        client.disconnect()
        print("The game was stopped, thank you for playing thr game")
    else:
        print(msg_payload)
    return

#------------------------------------------------------
# Process Outgoing Messages

# Add a user
def post_player(client,player):
    client.publish("new_game",player,qos=1)
    return

# Processing the sending of the outgoing message
def post_move(client, aMove):
    client.publish(f"games/{lobby_name}/{player_name}/move", aMove, qos=1)
    return

# Start the game
def post_start(client):
    client.publish(f"games/{lobby_name}/start", payload="START", qos=1)
    return

# Stop the game
def post_stop(client):
    client.publish(f"games/{lobby_name}/start", payload="STOP", qos=1)
    return

# Publishes the scores
def publish_scores(client, score):
    client.publish(f"games/{lobby_name}/scores",payload = json.dumps(score), qos=1)

#------------------------------------------------------
# Process Game Moves

# Create a list of 4 possible coordinates adjacent to the curent position
def possible_adjacent(aCoordinate):
    theList = []
    theList.append(([theMoves["UP"][0]+aCoordinate[0],theMoves["UP"][1]+aCoordinate[1]],"UP"))
    theList.append(([theMoves["DOWN"][0]+aCoordinate[0],theMoves["DOWN"][1]+aCoordinate[1]],"DOWN"))
    theList.append(([theMoves["LEFT"][0]+aCoordinate[0],theMoves["LEFT"][1]+aCoordinate[1]],"LEFT"))
    theList.append(([theMoves["RIGHT"][0]+aCoordinate[0],theMoves["RIGHT"][1]+aCoordinate[1]],"RIGHT"))
    return theList

def get_to_field(aList):
    for i in aList:
        aCoordinate = i[0]
        for j in aCoordinate:
            if (j<0) or (j>9):
                aList.remove(i)
    return aList

# Search adjacent coordinates for teammates, enemies, walls, if there is, remove
def avoid_obsticles(aList, aBoard):
    topics = ["teammatePositions","enemyPositions","walls"]
    for aTopic in topics:
        for aCoordinate in aBoard[aTopic]:
            for aMove in aList:
                i = aMove[0]
                if (i == aCoordinate):
                    aList.remove(aMove)
    return aList

            
# Search if the adjacent squares have a coin, choose the first highest coin there is
def look_for_coins(aList,aBoard):
    topics = ["coin3","coin2","coin1"]
    for aTopic in topics:
        for aCoordinate in aBoard[aTopic]:
            for aMove in aList:
                i = aMove[0]
                if (i == aCoordinate):
                    return aMove


# Requests the move from a function
def move_request(aBoard):
    aCurentPosition = aBoard["currentPosition"]
    possibleMoves = possible_adjacent(aCurentPosition)
    possibleMoves = get_to_field(possibleMoves)
    possibleMoves = avoid_obsticles(possibleMoves,aBoard)
    if (look_for_coins(possibleMoves,aBoard)):
        return look_for_coins(possibleMoves,aBoard)[1]
    elif (len(possibleMoves)>0):
        n = random.randint(1,len(possibleMoves))
        return possibleMoves[n-1][1]
    else:
        return "UP"

#------------------------------------------------------
# Dispatch the messages

dispatch = {
    'game_state' : game_state,
    'lobby' : lobby,
}

#------------------------------------------------------
# Main 

if __name__ == '__main__':

    #============================
    # Connect + set up the responce behaviour

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(theLogin, thePassword)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(theURL, 8883)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish
    
    #============================
    # Subscribe to the topics

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/{player_name}/game_state")

    #============================
    # Connect to the lobby + ask to start the game
    post_player(client,json.dumps({'lobby_name':lobby_name,'team_name':team_name ,'player_name' : player_name}))
    time.sleep(1)
    # post_start(client)
    time.sleep(1)
    client.loop_forever()
    