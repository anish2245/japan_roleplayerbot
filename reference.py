import json

def elicitIntent(intent_name, help_response):
    print("Inside Elicit Intent", help_response)
    response = {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitIntent"
            },
            "intent": {
                "name": intent_name
            }
        },
        "messages": [
            {
                "contentType": "CustomPayload",
                "content": json.dumps(help_response)
            }
        ]
    }
    return response

def validate_slots(intent_name, slots):
    if not slots["FromCity"]:
        print("From City Slot is empty, get the value")
        return {"isValid": False, "SlotToElicit": "FromCity"}
    
    if not slots["ToCity"]:
        print("To City Slot is empty, get the value")
        return {"isValid": False, "SlotToElicit": "ToCity"}

    if not slots["Date"]:
        print("Date Slot is empty, get the value")
        return {"isValid": False, "SlotToElicit": "Date"}
    
    if not slots["Passengers"]:
        print("Passengers Slot is empty, get the value")
        return {"isValid": False, "SlotToElicit": "Passengers"}
    
    session_attributes = {
        "FromCity": slots["FromCity"]["value"]["originalValue"],
        "ToCity": slots["ToCity"]["value"]["originalValue"],
        "Date": slots["Date"]["value"]["interpretedValue"],
        "Passengers": slots["Passengers"]["value"]["originalValue"]
    }

    return {"isValid": True, "session_attributes": session_attributes}

def elicitSlot(slotToElicit, intent_name, slots):
    response = {
        "sessionState": {
            "dialogAction": {
                "slotToElicit": slotToElicit,
                "type": "ElicitSlot"
            },
            "intent": {
                "name": intent_name,
                "slots": slots
            }
        }
    }
    return response

def closeIntent(intent_name, message):
    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_name,
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }
    return response

def lambda_handler(event, context):
    try:
        print("event--", json.dumps(event))
        
        # Extracting intent name and invocation source
        intent_name = event['sessionState']['intent']['name']
        invocation_source = event['invocationSource']
        slots = event['sessionState']['intent']['slots']

        # Check if invocation source is DialogCodeHook
        if invocation_source == "DialogCodeHook":
            response = None
            # Handle the Help intent if no slots are filled
            if intent_name == 'Help' and not slots:
                help_response = {
                    "templateType": "ListPicker",
                    "version": "1.0",
                    "data": {
                        "replyMessage": {
                            "title": "Thanks for Selecting!"
                        },
                        "content": {
                            "title": "How may I assist you?",
                            "subtitle": "Tap to select option",
                            "imageType": "URL",
                            "imageData": "https://www.goindigo.in/content/dam/indigov2/6e-website/downloadapp/Feature-Image.png",
                            "imageDescription": "Select any of the option",
                            "elements": [
                                {
                                    "title": "Book a Flight",
                                    "imageType": "URL",
                                    "imageData": "https://cdn0.iconfinder.com/data/icons/travel-line-color-this-is-vacation-time/512/Flight_booking-512.png"
                                },
                                {
                                    "title": "Flight Information",
                                    "imageType": "URL",
                                    "imageData": "https://static.thenounproject.com/png/3652216-200.png"
                                },
                                {
                                    "title": "Manage Booking",
                                    "imageType": "URL",
                                    "imageData": "https://cdn0.iconfinder.com/data/icons/miscellaneous-22-line/128/booking_travel_tourism_online_reservation_ticket_air-ticket-512.png",
                                    "imageDescription": "Banana"
                                },
                                {
                                    "title": "Contact Us",
                                    "imageType": "URL",
                                    "imageData": "https://cdn-icons-png.flaticon.com/512/3095/3095583.png",
                                    "imageDescription": "Banana"
                                }
                            ]
                        }
                    }
                }
                response = elicitIntent(intent_name, help_response)
                return response
            
            if intent_name == "BookaFlight":
                validate_response = validate_slots(intent_name, slots)
                if not validate_response["isValid"]:
                    elicitResponse = elicitSlot(validate_response["SlotToElicit"], intent_name, slots)
                    return elicitResponse
                
                if validate_response["isValid"]:
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "Delegate"
                            },
                            "intent": {
                                'name': intent_name,
                                'slots': slots
                            }
                        }
                    }
                    return response
        
        if invocation_source == "FulfillmentCodeHook":
            session_attributes = {
        "FromCity": slots["FromCity"]["value"]["originalValue"],
        "ToCity": slots["ToCity"]["value"]["originalValue"],
        "Date": slots["Date"]["value"]["interpretedValue"],
        "Passengers": slots["Passengers"]["value"]["originalValue"]
    }
            message = (
                f"Thank you! Your booking details are as follows:\n"
                f"From: {session_attributes['FromCity']}\n"
                f"To: {session_attributes['ToCity']}\n"
                f"Date: {session_attributes['Date']}\n"
                f"Passengers: {session_attributes['Passengers']}"
            )
            response = closeIntent(intent_name, message)
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred: {str(e)}')
        }
