import json


def elicitIntent(intent_name, welcome_response):
    print("Inside Elicit Intent", welcome_response)
    response = {
        "sessionState": {
            "dialogAction": {"type": "ElicitIntent"},
            "intent": {"name": intent_name},
        },
        "messages": [
            {"contentType": "CustomPayload", "content": json.dumps(welcome_response)}
        ],
    }
    return response


def ask_question(question, session_attributes,intent_name):
    print("Inside Ask Question",question)
    response = {
        "sessionState": {
            "dialogAction": {"type": "ElicitIntent"},
            "intent": {"name": intent_name},
        },
        "messages": [
            {"contentType": "PlainText", "content":question['questionText'] }
        ],
    }
    return response


def lambda_handler(event, context):
    try:
        print("event--", json.dumps(event))

        intent_name = event["sessionState"]["intent"]["name"]
        invocation_source = event["invocationSource"]
        session_attributes = event.get("sessionAttributes", {})
        input_text = event.get("inputTranscript", "").lower()
        print("Input text",input_text)

        print("Intent Name", intent_name)
        print("invocation Source", invocation_source)

        if invocation_source == "DialogCodeHook":
            response = None
            # Handle the Welcome Intent
            if intent_name == "WelcomeIntent":
                welcome_response = {
                    "templateType": "QuickReply",
                    "version": "1.0",
                    "data": {
                        "replyMessage": {
                            "title": "Here are the list of products you can select from!"
                        },
                        "content": {
                            "title": "Which department would you like?",
                            "elements": [{"title": "paracitomal"}, {"title": "Crozin"}],
                        },
                    },
                }
                response = elicitIntent(intent_name, welcome_response)
                return response
            if intent_name == "ProductsIntent":
                print("Inside Products intent",session_attributes)
                if "questionFlow" not in session_attributes:
                    print("Inside IF--")
                    # First interaction - determine product and fetch questions
                    product_type = None

                    if "paracitomal" in input_text:
                        product_type = "paracitomal"
                    elif "crozin" in input_text:
                        product_type = "crozin"

                    if not product_type:
                        # If product type couldn't be determined, ask for clarification
                        return {
                            "sessionAttributes": session_attributes,
                            "dialogAction": {
                                "type": "ElicitIntent",
                                "message": {
                                    "contentType": "PlainText",
                                    "content": "Please specify if you are asking about paracitomal or crozin.",
                                },
                            },
                        }

                    questions = [
                        {
                            "productType": "paracitomal",
                            "id": "1",
                            "questionText": "What is your age?",
                        },
                        {
                            "productType": "paracitomal",
                            "id": "2",
                            "questionText": "Have you used paracitomal before?",
                        },
                        {
                            "productType": "crozin",
                            "id": "1",
                            "questionText": "Do you have any allergies?",
                        },
                        {
                            "productType": "crozin",
                            "id": "2",
                            "questionText": "How long have you been experiencing symptoms?",
                        },
                    ]

                    session_attributes["questionFlow"] = "active"
                    session_attributes["productType"] = product_type
                    session_attributes["questions"] = json.dumps(questions)
                    session_attributes["currentQuestionIndex"] = "0"
                    session_attributes["answers"] = json.dumps([])

                    return ask_question(questions[0], session_attributes,intent_name)

                else:
                    print("in the Else block")
                    # We're in the middle of the question flow
                    questions = json.loads(session_attributes["questions"])
                    current_index = int(session_attributes["currentQuestionIndex"])
                    answers = json.loads(session_attributes["answers"])
                    print("Answers",answers)
                    # Store the user's answer to the current question
                    answers.append(
                        {
                            "question": questions[current_index]["text"],
                            "answer": input_text,
                        }
                    )
                    session_attributes["answers"] = json.dumps(answers)

                    if current_index + 1 < len(questions):
                        # Move to the next question
                        session_attributes["currentQuestionIndex"] = str(
                            current_index + 1
                        )
                        return ask_question(
                            questions[current_index + 1], session_attributes
                        )
                    else:
                        # All questions have been answered
                        # Process the collected answers (store in DynamoDB, etc.)
                        #store_answers(session_attributes["productType"], answers)

                        # Clear the question flow
                        session_attributes.pop("questionFlow", None)
                        session_attributes.pop("questions", None)
                        session_attributes.pop("currentQuestionIndex", None)

                        # End the conversation
                        return {
                            "sessionAttributes": session_attributes,
                            "dialogAction": {
                                "type": "Close",
                                "fulfillmentState": "Fulfilled",
                                "message": {
                                    "contentType": "PlainText",
                                    "content": f"Thank you for answering all the questions about {session_attributes['productType']}.",
                                },
                            },
                        }
            return {
                "sessionAttributes": session_attributes,
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled",
                    "message": {
                        "contentType": "PlainText",
                        "content": "I didn't understand that. Please try again.",
                    },
                },
            }

        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"An error occurred: {str(e)}")}
