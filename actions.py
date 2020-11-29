from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json
from collections import namedtuple
# Import smtplib for the actual sending function
import smtplib, ssl

# Import the email modules we'll need
from email.message import EmailMessage


class ActionValidLocation(Action):
    def __init__(self):
        self.config = {"user_key": "f4924dc9ad672ee8c4f8c84743301af5"}

    def name(self):
        return 'action_valid_location'

    def get_location_tier(self, location):
        # Tier1 cities
        tier1 = ["ahmedabad", "bengaluru", "bangalore", "chennai", "delhi", "hyderabad", "kolkata", "mumbai", "pune"]
        # Tier2 cities
        tier2 = ['agra', 'ajmer', 'aligarh', 'amravati', 'amritsar', 'asansol', 'aurangabad', 'bareilly',
                 'belgaum', 'bhavnagar', 'bhiwandi', 'bhopal', 'bhubaneswar', 'bikaner', 'bilaspur',
                 'bokaro steel city', 'chandigarh', 'coimbatore', 'cuttack', 'dehradun', 'dhanbad','bhilai',
                 'durgapur', 'dindigul', 'erode', 'faridabad', 'firozabad', 'ghaziabad', 'gorakhpur',
                 'gulbarga', 'guntur', 'gwalior', 'gurgaon', 'guwahati', 'hamirpur', 'hubli–dharwad', 'indore',
                 'jabalpur', 'jaipur', 'jalandhar', 'jammu', 'jamnagar', 'jamshedpur', 'jhansi', 'jodhpur',
                 'kakinada', 'kannur', 'kanpur', 'karnal', 'kochi', 'kolhapur', 'kollam', 'kozhikode',
                 'kurnool', 'ludhiana', 'lucknow', 'madurai', 'malappuram', 'mathura', 'mangalore', 'meerut',
                 'moradabad', 'mysore', 'nagpur', 'nanded', 'nashik', 'nellore', 'noida', 'patna',
                 'pondicherry', 'purulia', 'prayagraj', 'raipur', 'rajkot', 'rajahmundry', 'ranchi',
                 'rourkela', 'salem', 'sangli', 'shimla', 'siliguri', 'solapur', 'srinagar', 'surat',
                 'thanjavur', 'thiruvananthapuram', 'thrissur', 'tiruchirappalli', 'tirunelveli', 'ujjain',
                 'bijapur', 'vadodara', 'varanasi', 'vasai-virar city', 'vijayawada', 'visakhapatnam',
                 'vellore', 'warangal']


        zomato = zomatopy.initialize_app(self.config)
        location = location.lower()
        location_response = zomato.get_location(location, 1)
        location_json = json.loads(location_response)
        location_suggestions_len = len(location_json['location_suggestions'])

        if location.lower() in tier1:
            return [SlotSet('location', location), SlotSet('location_cat', "tier1")]
        elif location.lower() in tier2:
            return [SlotSet('location', location), SlotSet('location_cat', "tier2")]
        elif location_suggestions_len==0 or location not in map(str.lower, location_json["location_suggestions"][0]["city_name"].split()):
            return [SlotSet('location', None), SlotSet('location_cat', "other")]
        else:
            return [SlotSet('location', None), SlotSet('location_cat', "tier3")]

    def run(self, dispatcher, tracker, domain):
        location = tracker.get_slot('location')
        return self.get_location_tier(location)

class ActionSearchRestaurants(ActionValidLocation):

    def __init__(self):
        super().__init__()
        self.cuisines_dict = {'chinese': 25, 'mexican': 73,
                              'italian': 55, 'american': 1,
                              'south indian': 85, 'north indian': 50}

    def name(self):
        return 'action_search_restaurants'

    def get_budget(self, budget):
        if budget == "lesser than rs 300":
            return lambda avg_price: avg_price<300
        elif budget == "rs 300 to 700":
            return lambda avg_price: avg_price >=300 and avg_price<=700
        else:
            return lambda avg_price: avg_price>700

    def run(self, dispatcher, tracker, domain):
        zomato = zomatopy.initialize_app(self.config)
        location = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine').lower()
        global budget
        budget = tracker.get_slot('budget').lower()
        location_response = zomato.get_location(location, 1)
        location_json = json.loads(location_response)
        lat = location_json["location_suggestions"][0]["latitude"]
        lon = location_json["location_suggestions"][0]["longitude"]

        restaurants = zomato.restaurant_search("", lat, lon, str(self.cuisines_dict.get(cuisine)), sort="rating", order="desc", limit=200)
        restaurants_json = json.loads(restaurants)
        Restaurant = namedtuple("Restaurant", "name rating address budget")

        global restaurant_result
        restaurant_result = []
        if restaurants_json['results_found'] == 0:
            response = "No restaurants found based on your query!, try other cuisines or budget!"
            dispatcher.utter_message(response)
            return[SlotSet('cuisine', None), SlotSet('budget', None)]
        else:
            for restaurant in restaurants_json['restaurants']:
                if self.get_budget(budget)(restaurant['restaurant']['average_cost_for_two']) and len(restaurant_result)<=10:
                    restaurant_result.append(Restaurant(restaurant['restaurant']['name'],
                                                       restaurant['restaurant']['user_rating']['aggregate_rating'],
                                                       restaurant['restaurant']['location']['address'],
                                                       restaurant['restaurant']['average_cost_for_two']))
            response = ""
            if len(restaurant_result) == 0:
                response = "No restaurants found based on your query!, try other cuisines or budget!"
                dispatcher.utter_message(response)
                return [SlotSet('cuisine', None), SlotSet('budget', None)]
            else:
                for restro in restaurant_result[:5]:
                    response += restro.name + f" (rating: {restro.rating}) in " + restro.address +\
                                f". And the average price for two people here is: {restro.budget}\n"

                response = f"Showing you top rated restaurants based on your budget {budget}:\n" + response

                dispatcher.utter_message(response)

class ActionSendEmail(ActionSearchRestaurants):

    def name(self):
        return 'action_send_email'

    def run(self, dispatcher, tracker, domain):
        email = tracker.get_slot('email')

        message = ""
        for restro in restaurant_result[:10]:
            message += restro.name + f" (rating: {restro.rating}) in " + restro.address +\
                        f". And the average price for two people here is: {restro.budget}\n"


        message = f"Showing you top rated restaurants based on your budget {budget}:\n" + message
        msg = EmailMessage()
        msg.set_content(message)

        msg['Subject'] = 'Restaurant results'
        msg['From'] = <email>
        msg['To'] = email

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('smtp.gmail.com', 587)
        context = ssl.create_default_context()
        s.starttls(context=context)
        s.login(<email>, <password>)
        s.send_message(msg)
        s.quit()
        dispatcher.utter_message("Sent!")
