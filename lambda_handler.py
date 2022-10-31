# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the implementation of handler classes approach in skill builder.
import logging

import boto3

from urllib.request import Request

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_account_linking_access_token, get_request_type, get_intent_name, get_slot_value_v2, get_simple_slot_values 
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard, output_speech
from ask_sdk_model import Response


cognito_client = boto3.client('cognito-idp')
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CheckAccountLinkedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return not get_account_linking_access_token(handler_input)
        
        
    def handle(self, handler_input):
        return handler_input.response_builder.speak("Need to link account in Alexa App").response

class SayHelloHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return get_request_type(handler_input) == "IntentRequest" and get_intent_name(handler_input) == 'SayHelloIntent'
    def handle(self, handler_input):
        reprompt_message = "what is your request?"
        speak_message = "hello " + get_user_name(handler_input)
        return handler_input.response_builder.speak(speak_message).ask(reprompt_message).response


class RequestInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        print("handler input is: ")

        print(handler_input)

        return is_request_type("IntentRequest")(handler_input) and is_intent_name("RequestInfoIntent")(handler_input)

    def handle(self, handler_input):

        output_string = "Email: " + get_user_email(handler_input) + " Full Name: " + get_user_full_name(handler_input)
        return handler_input.response_builder.speak("Here is your info, " + output_speech).set_card(
            SimpleCard("Hello" + get_user_name(handler_input), output_string)
        ).response

        

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Hello World skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


def get_user_email(handler_input):
    user_infos = cognito_client.get_user(AccessToken=get_account_linking_access_token(handler_input))['UserAttributes']

    user_info_dic = {}
    for user_info in user_infos:
        user_info_dic[user_info['Name']] = user_info['Value']
    return user_info_dic['email']

def get_user_full_name(handler_input):
    user_infos = cognito_client.get_user(AccessToken=get_account_linking_access_token(handler_input))['UserAttributes']

    user_info_dic = {}
    for user_info in user_infos:
        user_info_dic[user_info['Name']] = user_info['Value']
    return user_info_dic['name']

def get_user_name(handler_input):
    return cognito_client.get_user(AccessToken=get_account_linking_access_token(handler_input))['Username']


sb.add_request_handler(CheckAccountLinkedHandler())
sb.add_request_handler(SayHelloHandler())
sb.add_request_handler(RequestInfoHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
