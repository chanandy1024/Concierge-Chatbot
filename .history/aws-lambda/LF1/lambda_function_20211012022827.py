import json
import random
import decimal
import time
import datetime
import dateutil.parser
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def isvalid_city(city):
    valid_cities = ['the bronx', 'brooklyn', 'manhattan', 'queens', 'staten island', 'lic', 'bronx']
    return city.lower() in valid_cities


def isvalid_cuisine_type(cuisine_type):
    cuisine_types = ['pizza', 'chinese', 'burgers', 'american', 'delis', 'italian',
                    'fast food', 'seafood', 'barbeque', 'caribbean', 'japanese', 'mexican', 'salad', 'sushi',
                    'bars', 'latin american', 'korean diners', 'asian fusion', 'specialty food', 'cafes', 'thai',
                    'steakhouses', 'desserts', 'halal', 'spanish', 'noodles', 'mediterranean', 'comfort food',
                    'soup', 'indian', 'soul food', 'dominican', 'vegan', 'vietnamese', 'ramen', 'hot dogs',
                    'vegetarian', 'greek', 'dim sum', 'portuguese', 'southern', 'cantonese', 'middle eastern', 
                    'cajun/creole', 'bubble tea', 'beer, wine & spirits', 'irish', 'cuban', 'tapas/small plates', 
                    'filipino', 'szechuan', 'colombian', 'french', 'tacos', 'brazilian', 'gluten-free', 'irish'
                    'pub', 'empanadas', 'peruvian', 'tapas', 'bars', 'pasta', 'shops', 'hot pot']
    return cuisine_type.lower() in cuisine_types


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        
def isvalid_phoneNumber(phoneNumber):
    return len(phoneNumber) == 10


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate(city, cuisine_type, date, phoneNumber):
    if city and not isvalid_city(city):
        return build_validation_result(False, 'City', 'We currently do not support {} as a valid destination. Can you try a different area?'.format(city))
    if date:
        print(datetime.datetime.strptime(date, '%Y-%m-%d'))
        print(datetime.date.today())
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand your arrival date.  When would you like to dine in?')
        if datetime.datetime.strptime(date, '%Y-%m-%d').date() + timedelta(hours=3) < datetime.date.today():
            return build_validation_result(False, 'Date', 'Reservations must be scheduled today or after. Can you try a different date?')

    if cuisine_type and not isvalid_cuisine_type(cuisine_type):
        return build_validation_result(False, 'Cuisine', 'I did not understand your cuisine preference.  What cuisine would you like to try?')
    
    if phoneNumber and not isvalid_phoneNumber(phoneNumber):
        return build_validation_result(False, 'PhoneNumber', 'Please enter a valid ten-digit phone number.')
                
    return {'isValid': True}


def get_session_attributes(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return session_attributes


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def get_slot(intent_request, slot):
    return intent_request['currentIntent']['slots'][slot]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
    

""" --- Main Functions that are hooked with intents --- """

def Greeting(intent_request):
    session_attributes = get_session_attributes(intent_request)
    text = "Hi there, I'm your dining concierge, what can I help you with today?"
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(session_attributes, fulfillment_state, message)   

def DiningSuggestions(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    city = get_slot(intent_request, 'City')
    cuisine = get_slot(intent_request, 'Cuisine')
    attendees = get_slot(intent_request, 'Attendees')
    date = get_slot(intent_request, 'Date')
    time = get_slot(intent_request, 'Time')
    phoneNumber = get_slot(intent_request, 'PhoneNumber')
    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate(city, cuisine, date, phoneNumber)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        if confirmation_status == 'Denied':
            message = {
                        'contentType': 'PlainText',
                        'content': 'Ok, your request is cancelled.'
                    }
            return close(session_attributes, "Fulfilled", message)
        else:
            
            return delegate(session_attributes, intent_request['currentIntent']['slots'])
            
    '''send message to sqs queue'''
    sqs_client = boto3.client("sqs", region_name="us-west-2")
    
    all_slots = get_slots(intent_request)
    all_slots['user_id'] = intent_request['userId']
    
    response = sqs_client.send_message(
        QueueUrl="https://sqs.us-west-2.amazonaws.com/164008855428/diningQueue.fifo",
        MessageBody=json.dumps(all_slots),
        MessageGroupId="diningRequestParams"
    )
    text = "You’re all set. Expect my suggestions shortly! Have a good day."
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(session_attributes, fulfillment_state, message)

def ThankYou(intent_request):
    session_attributes = get_session_attributes(intent_request)
    text = "Thank you, have a nice day!"
    message = {
        'contentType': 'PlainText',
        'content': text,
    }
    fulfillment_state = "Fulfilled"
    
    return close(session_attributes, fulfillment_state, message)

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    # Dispatch to the bot's intent handlers
    logger.debug('intent:{}'.format(intent_name))
    if intent_name == 'Greeting':
        return Greeting(intent_request)
    elif intent_name == 'DiningSuggestions':
        return DiningSuggestions(intent_request)
    elif intent_name == 'ThankYou':
        return ThankYou(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    response = dispatch(event)
    print(response)
    logger.debug(response)
    return response
