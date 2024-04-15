import json
import time
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
team_name1 = "team2"
player_name = "player2"

# Moves
theMoves = {
    "UP" : (-1, 0),
    "DOWN" : (1, 0),
    "LEFT" : (0, -1),
    "RIGHT" : (0, 1)
}

aPreviousMove = {}

theScores = {
    team_name: 0,
    team_name1: 0
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
    # get_scores(aCurentMove)
    print(aCurentMove)
    # publish_scores(client,theScores)
    # Process the game state to the user
    display_board(aCurentMove)
    #Request next move
    anInput,inputType = move_request(aCurentMove)

    if inputType == "moves":
        post_move(client, anInput)
    elif inputType == "stop":
        post_stop(client)

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

# Requests the move from the user
def move_request(aBoard):
    # Pring instructions
    print("----------------------------------------")
    print("Available moves: UP, DOWN, LEFT, RIGHT \nSubmit STOP to stop the game")
    print("----------------------------------------")
    # Get Input
    anInput = input('Please Enter your move: ')
    # Process the input
    if anInput in theMoves:
        return anInput,"moves"
    elif anInput == "STOP":
        return "stop","stop"
    else: 
        print("Incorrect Input")
    return

# Provides a terminal GUI of the curent position of the board 
def display_board(aBoard):
    return

# Finds the elements that are different 
def mising_links(aList1, aList2):
    print("--------------------------------------------------")
    print(aList1,aList2)
    aMissingList = []
    j = 0
    if(len(aList2) == 0):
        return aList1
    for i in range(len(aList2)):
        while (aList1[i+j]!=aList2[i]):
            aMissingList.append(aList1[i+j])
            j+=1
        if(i+1 == len(aList2)):
            aMissingList+=aList1[(i+j+1):len(aList1)]
    return aMissingList

# Find the users that collected the coin
def find_a_collector(aCoinCoordinate,aCurentMove):
    aPlayerList = ["teammatePositions","enemyPositions"]
    # Check if the teammate or enemy collected the coin
    for kind in aPlayerList:
        for aTeamLcation in aCurentMove[kind]:
            if aTeamLcation == aCoinCoordinate:
                return kind
    # Check if thge user collected the coin
    if aCurentMove["currentPosition"] == aCoinCoordinate:
        return "currentPosition"
    
# Copy one Json object to another
def copy_json(aJsonOriginal,aJsonCopy):
    for keys in aJsonOriginal:
        aJsonCopy[keys] = aJsonOriginal[keys]
    return

# Updates the scores for the lobby
def get_scores(aCurentMove):
    if (len(aPreviousMove)) != 0:
        for i in range(3):
            if len(aPreviousMove["coin"+str(i+1)]) != len(aCurentMove["coin"+str(i+1)]):
                # Get the list of coins of the value
                aCollectedCoinIList = mising_links(aPreviousMove["coin"+str(i+1)],aCurentMove["coin"+str(i+1)])
                for aCoordinate in aCollectedCoinIList:
                    aKind = find_a_collector(aCoordinate,aCurentMove)
                    if (aKind == "teammatePositions" or aKind == "currentPosition"):
                        theScores[team_name]+=i
                    elif (aKind == "enemyPositions"):
                        theScores[team_name]+=i
                        
    copy_json(aCurentMove,aPreviousMove)
    return

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
    