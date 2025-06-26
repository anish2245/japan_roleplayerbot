import json

questions = [
    {
        "productType": "paracitomal",
        "id": "1",
        "questionText": "What is your age?",
        "answer":"45"
    },
    {
        "productType": "paracitomal",
        "id": "2",
        "questionText": "Have you used paracitomal before?",
        "answer":"NO"
    },
    {
        "productType": "paracitomal",
        "id": "3",
        "questionText": "What is the recommended dosage of paracetamol for adults?",
        "answer":"35"
    }
]

def ask_next_question_with_ack(intent_name, session_attributes, current_question_index, user_answer=None):
    current_question = questions[current_question_index]
    session_attributes["current_question_index"] = str(current_question_index)

    messages = []

    if user_answer:
        # Acknowledge the answer
        messages.append({
            "contentType": "PlainText",
            "content": f"You said: {user_answer}"
        })

    # Ask the next question
    messages.append({
        "contentType": "PlainText",
        "content": current_question["questionText"]
    })

    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": "AnswerSlot"
            },
            "intent": {
                "name": intent_name,
                "slots": {
                    "AnswerSlot": None
                },
                "state": "InProgress"
            },
            "sessionAttributes": session_attributes
        },
        "messages": messages
    }

def lambda_handler(event, context):
    try:
        print("event--", json.dumps(event))

        intent_name = event["sessionState"]["intent"]["name"]
        invocation_source = event["invocationSource"]
        session_attributes = event["sessionState"].get("sessionAttributes", {})

        print("Intent Name-->", intent_name)
        print("invocation_source-->", invocation_source)
        print("session_attributes outside the IF-->", session_attributes)

        if invocation_source == "DialogCodeHook":

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
                return {
                    "sessionState": {
                        "dialogAction": {"type": "ElicitIntent"},
                        "intent": {"name": intent_name},
                    },
                    "messages": [
                        {
                            "contentType": "CustomPayload",
                            "content": json.dumps(welcome_response)
                        }
                    ],
                }

            elif intent_name == "ProductsIntent":
                print("session_attributes Inside the Product Intent-->", session_attributes)
                current_index = int(session_attributes.get("current_question_index", "-1"))
                print("current_index", current_index)

                if current_index == -1:
                    # First time entry
                    return ask_next_question_with_ack(intent_name, session_attributes, 0)

                # Save previous answer
                previous_question = questions[current_index]
                user_answer = event["inputTranscript"]

                print("user_answer-->", user_answer)
                session_attributes[f"answer_{previous_question['id']}"] = user_answer
                print("session_attributes after answer", session_attributes)

                next_index = current_index + 1
                if next_index < len(questions):
                    return ask_next_question_with_ack(intent_name, session_attributes, next_index, user_answer)
                else:
                    # All questions completed
                    summary = "\n".join([
                        f"Q: {q['questionText']} A: {session_attributes.get(f'answer_{q['id']}', '')}"
                        for q in questions
                    ])
                    print("Summary -->", summary)
                    return {
                        "sessionState": {
                            "dialogAction": {"type": "Close"},
                            "intent": {
                                "name": intent_name,
                                "state": "Fulfilled"
                            },
                            "sessionAttributes": session_attributes
                        },
                        "messages": [
                            {
                                "contentType": "PlainText",
                                "content": "Thanks for your responses!\n" + summary
                            }
                        ]
                    }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"An error occurred: {str(e)}")
        }
