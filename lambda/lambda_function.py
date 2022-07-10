# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils
import requests as req
import prompts
import random
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor
from ask_sdk_core.utils import is_intent_name, get_slot_value, get_user_id, is_request_type#, get_dialog_state
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, DialogState


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class LaunchRequestHandler(AbstractRequestHandler):
    
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input) 

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        data = handler_input.attributes_manager.request_attributes["_"]

        reprompt = data[prompts.HELP_REPROMPT]

        user_id = get_user_id(handler_input)
        device_id = handler_input.request_envelope.context.system.device.device_id
        
        #API Schnittstelle für add Session ID
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_data.php?command=add&deviceid={}'.format(device_id)
        req.post(urladd)

        # API Schnittstelle für GET username
        urlgetData = 'https://vokabeltrainer.dipferlscheisser.de/API/apiGetDataLastSession.php?command=getLastSession&deviceid={}'.format(device_id)
        param=dict()
        resp = req.get(url=urlgetData, params=param)
        data = resp.json()
        dbuser = (data["lastusername"])
        dbschool = (data["lastschool"])
        dbclass = (data["class"])
        dblanguage = (data["lastlanguage"])
        dbunit = (data["lastunit"])
        dbchapter = (data["lastchapter"])
        
        if dbschool == "gymnasium":
         #   speak_output = data[prompts.WELCOME_BACK_MESSAGE].format(dbuser)## + data[prompts.WELCOME_BACK_REALSCHULE_MESSAGE].format(dbschool) + data[prompts.WELCOME_BACK_CLASS_MESSAGE].format(dbclass) + data[prompts.WELCOME_BACK_WORDSCHATZ_MESSAGE].format(dbunit) + data[prompts.REQUEST_CONTINUE_GYM_MESSAGE]
            speak_output = "Hallo {}, schön dass du wieder hier bist!".format(dbuser)+" Wenn ich mich richtig erinnere, dann besuchst du aktuell das {}.".format(dbschool)+" und bist in der {}ten Klasse.".format(dbclass)+" Beim letzten Mal haben wir gemeinsam {} trainiert.".format(dblanguage)+" Wir waren bei der {}".format(dbunit)+" im Kapitel: {}.".format(dbchapter)+" Möchtest du hier weitermachen oder ein neues Kapitel beginnen?"
        
        elif dbschool == "mittelschule":
            speak_output =  "Hallo {}, schön dass du wieder hier bist!".format(dbuser)+"Wenn ich mich richtig erinnere, dann besuchst du aktuell die {}.".format(dbschool)+" und bist in der {}ten Klasse.".format(dbclass)+" Beim letzten Mal haben wir gemeinsam {} trainiert.".format(dblanguage)+" Wir waren bei der {}".format(dbunit)+" im Kapitel: {}".format(dbchapter)+". Möchtest du hier weitermachen oder ein neues Kapitel beginnen?"
        
        elif dbschool == "realschule":
            speak_output =  data[prompts.WELCOME_BACK_MESSAGE].format(dbuser) + data[prompts.WELCOME_BACK_REALSCHULE_MESSAGE].format(dbschool) + data[prompts.WELCOME_BACK_CLASS_MESSAGE].format(dbclass) + data[prompts.WELCOME_BACK_UNIT_MESSAGE].format(dbunit) + data[prompts.REQUEST_CONTINUE_NO_GYM_MESSAGE]
        #    speak_output = "Hallo {}, schön dass du wieder hier bist!".format(dbuser)+"Wenn ich mich richtig erinnere, dann besuchst du aktuell die {}.".format(dbschool)+" und bist in der {}ten Klasse.".format(dbclass)+" Beim letzten Mal haben wir gemeinsam {} trainiert.".format(dblanguage)+" Wir waren bei der {}".format(dbunit)+" im Kapitel: {}.".format(dbchapter)+" Möchtest du hier weitermachen oder ein neues Kapitel beginnen?"
        
        else:
            speak_output = "Hallo und herzlich willkommen bei deinem persönlichen Vokabeltrainer für deine Schule. Damit dieses Training ein bißchen persönlicher von stattengeht, würde ich gerne deinen Namen wissen. Wie heißt du?" 
            #speak_output = "<speak><voice name="Kendra"> I am going to spell out Hello as <say-as interpret-as="spell-out">hello</say-as>. Now and then, I speak <voice name="Hans"><lang xml:lang="de-DE">Deutsch</lang></voice> and <voice name="Celine"><lang xml:lang="fr-FR">français</lang></voice> and  <voice name="Enrique"><lang xml:lang="es-ES">español</lang>.</voice></voice></speak>"
        repromt_text = "Ich habe dich anscheinend nicht richtig verstanden. Könntest du mir bitte noch einmal deinen Vornamen nennen?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )

class GetUserNameIntentHandler(AbstractRequestHandler):
    """Handler for Get Language Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetUserNameIntent")(handler_input) 
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        

        data = handler_input.attributes_manager.request_attributes["_"]

        username = get_slot_value(handler_input=handler_input, slot_name="firstname")
        

        repromt_text = "Könntest du bitte deinen Namen wiederholen?"

         #API Schnittstelle für Language
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_user.php?command=add&deviceid={}'.format(device_id) + '&username={}'.format(username)
        req.post(urladd)

        speak_output = ("Hallo {}, schön dass du heute mit mir trainieren möchtest. Um deinen Vokabelbereich genauer auf deine Bedürfnisse anzupassen, "
                        "würde ich gerne wissen welche Schule du besuchst. Auf welche Schule gehst du aktuell?".format(username))
        
        
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )

class CaptureSchoolTypeIntentHandler(AbstractRequestHandler):
    """Handler for Capture Schooltype Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureSchoolTypeIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        repromt_text = "Könntest du mir bitte deine Schulart nennen, damit wir auch die richtigen Vokabeln trainieren können. Zur Auswahl stehen: Mittelschule, Realschule und Gymnasium!"
        school = get_slot_value(handler_input=handler_input, slot_name="school")

         #API Schnittstelle für Session ID
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_school.php?command=add&deviceid={}'.format(device_id) + '&school={}'.format(school)
        req.post(urladd)

        if school.lower() == "realschule": 
            speak_output = "OK, willkommen bei deinem Vokabeltrainer für die {}. Welche Sprache möchtest du heute trainieren? Zur Auswahl stehen Englisch und Französisch.".format(school)
        
        elif school.lower() == "mittelschule":
            speak_output = "OK, willkommen bei deinem Vokabeltrainer für die {}. Welche Sprache möchtest du heute trainieren? Zur Auswahl steht Englisch.".format(school)
            
        elif school.lower() == "gymnasium":
            speak_output = "OK, willkommen bei deinem Vokabeltrainer für das {}. Welche Sprache möchtest du heute trainieren? Zur Auswahl stehen Englisch, Latein und Französisch.".format(school)
            
        else:
            speak_output = "Ich habe dich anscheinend nicht richtig verstanden. Könntest du mir bitte deine Schulart nennen, damit wir auch die richtigen Vokabeln trainieren können. Zur Auswahl stehen: Mittelschule, Realschule und Gymnasium!"
            
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )

class GetLanguageIntentHandler(AbstractRequestHandler):
    """Handler for Get Language Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetLanguageIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        session_attr = handler_input.attributes_manager.session_attributes
        language = get_slot_value(handler_input=handler_input, slot_name="language")
        repromt_text = "Könntest du mir bitte die gewünschte Fremdsprache wiederholen?"

         #API Schnittstelle für Language
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_language.php?command=add&deviceid={}'.format(device_id) + '&foreign_language={}'.format(language)
        req.post(urladd)

        speak_output = "OK. Du möchtest heute also {} trainieren. Für welche Klasse soll ich die Vokabeln vorbereiten?".format(language)
                    
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )

class GetKlassenIntentHandler(AbstractRequestHandler):
    """Handler for Get Class Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetKlassenIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        klassenstufe = get_slot_value(handler_input=handler_input, slot_name="klasse")
        repromt_text = "Könntest du mir bitte deine Klasse nennen"      
        
        #API Schnittstelle für Class
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_class.php?command=add&deviceid={}'.format(device_id) + '&klasse={}'.format(klassenstufe)
        req.post(urladd)

         # GET Data from Database for School
        urlgetschool = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getschool&deviceid={}'.format(device_id)
        urlgetlanguage = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getlanguage&deviceid={}'.format(device_id)
        responseschool = req.get(urlgetschool)
        responselanguage = req.get(urlgetlanguage)
        if responseschool.status_code == 200:
            dbschool = responseschool.text 
            dblanguage = responselanguage.text

            if dbschool.lower() == "gymnasium" and (dblanguage.lower() == "latein" or dblanguage.lower() == "lateinisch"):
                speak_output = "Alles klar. Du gehst also in die {}te Klasse. Welchen Wortschatz möchtest du heute trainieren? Bitte verwende folgendes Format: Wortschatz und dann die Nummer.".format(klassenstufe)
            else:
                speak_output = "Alles klar. Du gehst also in die {}te Klasse. Welche Unit möchtest du heute trainieren? Bitte verwende folgendes Format: Unit und dann die Nummer.".format(klassenstufe)
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )
class GetUnitIntentHandler(AbstractRequestHandler):
    """Handler for Get Unit Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetUnitIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        unitnumber = get_slot_value(handler_input=handler_input, slot_name="unit")

        #API Schnittstelle für unit
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_unit.php?command=add&deviceid={}'.format(device_id) + '&unit={}'.format(unitnumber)
        req.post(urladd)

        # GET Data from Database for School
        urlgetschool = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getschool&deviceid={}'.format(device_id)
        urlgetlanguage = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getlanguage&deviceid={}'.format(device_id)
        responseschool = req.get(urlgetschool)
        responselanguage = req.get(urlgetlanguage)

        if responseschool.status_code == 200:
            dbschool = responseschool.text 
            dblanguage = responselanguage.text

            if dbschool.lower() == "gymnasium" and (dblanguage.lower() == "latein" or dblanguage.lower() == "lateinisch"):
                speak_output = "Habe verstanden. Du möchtest den {} trainieren. Alea iacta est. Incipiamus.".format(unitnumber)
                repromt_text = "Könntest du mir bitte den gewünschten Wortschatz nennen!" 
            else:
                speak_output = "Habe verstanden. Du möchtest die {} trainieren. Welches Chapter wollen wir heute in Angriff nehmen? Bitte gib den namen des Kapitels an. Zum Beispiel: Skills oder Station 1".format(unitnumber)
                repromt_text = "Könntest du mir bitte die gewünschte Unit nennen!" 
        
                   
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )

class GetChapterIntentHandler(AbstractRequestHandler):
    """Handler for Get Unit Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetChapterIntent")(handler_input)
    
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        chapternumber = get_slot_value(handler_input=handler_input, slot_name="chapter")
        repromt_text = "Könntest du mir bitte die gewünschte Chapter nennen"

        #API Schnittstelle für chapter
        device_id = handler_input.request_envelope.context.system.device.device_id
        urladd = 'https://vokabeltrainer.dipferlscheisser.de/add_chapter.php?command=add&deviceid={}'.format(device_id) + '&chapter={}'.format(chapternumber)
        req.post(urladd)

        speak_output = data[prompts.GET_CHAPTER_MESSAGE].format(chapternumber)
                   
        return ( 
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )
class EnglishIntentHandler(AbstractRequestHandler):
    """Handler for asking english vocabulary"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EnglishIntent")(handler_input)

    def handle(self, handler_input):

        #add attributes for question and counters
        #attr = handler_input.attributes_manager.session_attributes
        #attr["counter"] = 0
        #attr["correct"] = 0
        #attr["wrong"] = 0

        # GET Data from Database for School
        device_id = handler_input.request_envelope.context.system.device.device_id
        urlgetclass = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getclass&deviceid={}'.format(device_id)
        urlgetunit = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getunit&deviceid={}'.format(device_id)
        urlgetchapter = 'https://vokabeltrainer.dipferlscheisser.de/get_data.php?command=getchapter&deviceid={}'.format(device_id)

        responseclass = req.get(urlgetclass)
        responseunit = req.get(urlgetunit)
        responsechapter = req.get(urlgetchapter)

        dbclass = responseclass.text
        dbunit = responseunit.text
        dbchapter = responsechapter.text

        # get englisch word
        urlgetenglisch = 'https://vokabeltrainer.dipferlscheisser.de/get_englisch.php?command=getenglisch&klasse={}'.format(dbclass) +'&unit={}'.format(dbunit) + '&chapter={}'.format(dbchapter)
        responseenglisch = req.get(urlgetenglisch)
        dbenglisch = responseenglisch.text

        # get count of words
        urlgetcounter = 'https://vokabeltrainer.dipferlscheisser.de/get_englisch_counter.php?command=getcount&klasse={}'.format(dbclass) +'&unit={}'.format(dbunit) + '&chapter={}'.format(dbchapter)
        responsecount = req.get(urlgetcounter)
        dbcount = responsecount.text

        # get german word
        urlgetgerman = 'https://vokabeltrainer.dipferlscheisser.de/get_german.php?command=getgerman&englisch={}'.format(dbenglisch)
        responsegerman = req.get(urlgetgerman)
        dbgerman = responsegerman.text

        if responseenglisch.status_code == 200:
            dbenglisch = responseenglisch.text 
            dbgerman = responsegerman.text
            dbcount = responsecount.text
        data = handler_input.attributes_manager.request_attributes["_"]
        
        speak_output = data[prompts.START_ENGLISCH_SESSION].format(dbcount)
        reprompt_text = data[prompts.ASK_ENGLISCH_WORD].format(dbenglisch)
        counter = dbcount
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(reprompt_text)
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
         # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.HELP_MESSAGE]
        reprompt = data[prompts.HELP_REPROMPT]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.STOP_MESSAGE]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale[:2]))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = language_data[locale[:2]]
        # if a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.
        speak_output = "Servus, machs gut bis zum nächsten Mal!"
        return (
            handler_input.response_builder.response
            .speak(speak_output)
            .response)


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Öha, anscheinend hat da gerade etwas gar nicht gefunzt."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

# Register GetRequest Handler für die Datenerfassung
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetUserNameIntentHandler())
sb.add_request_handler(CaptureSchoolTypeIntentHandler())
sb.add_request_handler(GetLanguageIntentHandler())
sb.add_request_handler(GetKlassenIntentHandler())
sb.add_request_handler(GetUnitIntentHandler())
sb.add_request_handler(GetChapterIntentHandler())
sb.add_request_handler(EnglishIntentHandler())

# Register default Handler
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())

sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()



"""
import requests as req
urlgetData = 'https://vokabeltrainer.dipferlscheisser.de/API/apiGetDataLastSession.php?command=getLastSession&deviceid=amzn1.ask.device.AFGP3BVF54JL67VNKWV5VVG4ZR2BD47BM6A5XLZY6M7V4IDCQRWR7ERWG7HHPYRKNQQRPFCK6JRE23XXSLPCIEDHAG5BHNTEG56YS6CLK72BHDXKAT3RUAJIXHQSNCGHPEOZHPWAXOX7CA4LFL4M6JDQHNB45MQJYBENON6REU5RRVVPEFCWS'
param=dict()
resp = req.get(url=urlgetData, params=param)
data = resp.json()
dbuser = (data["lastusername"])
dbschool = (data["lastschool"])
dbclass = (data["class"])
dblanguage = (data["lastlanguage"])
dbunit = (data["lastunit"])
dbchapter = (data["lastchapter"])

print(dbuser, " ", dbschool, " ", dbclass, " ", dblanguage,  " ", dbunit, " ", dbchapter)
"""