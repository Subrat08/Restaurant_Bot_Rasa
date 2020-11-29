# Restaurant Chatbot

This restaurant bot is made to help customers to find restaurants based on their desired cuisine and budget in their locality. And this bot is a part of course (PG Diploma) curriculum provided by Upgrad in asscoiation with IIITB. 
# Rasa Installation
 * Click [here](https://rasa.com/docs/rasa/installation/) and follow the installation guide.
# How to train and run the chatbot

  - Make changes to action.py file: Mention the email Id (<email>) and Password (<password>) to send emails to the customers.
  - Now, open up the command prompt or terminal and navigate to the path where restaurant chat bot folder is present.
  - Run below command to train the bot
      ```sh
    rasa train
    ```
  - Run below command to run action.py file
      ```sh
    rasa run actions
    ```
  - To interact with the bot, run the below command (make sure rasa run actions is already running in other terminal)
      ```sh
    rasa shell
    ```
  - In order to make new stores interactively, run below command
    (If model is not trained already)
      ```sh
    rasa interactive
    ```
    (If model is already trained, replace <modelname.tar> with the latest model)
      ```sh
    rasa interactive --model ./models/<modelname.tar>
    ```

## Important Files 
 * [nlu.yml](https://github.com/Subrat08/Restaurant_Bot_Rasa/blob/master/data/nlu.yml) : This file contains all the text which a user can say to the bot based on which itent and entities will be identified.
 * [stories.yml](https://github.com/Subrat08/Restaurant_Bot_Rasa/blob/master/data/stories.yml): This file consists different stories (dialouge flow).
 * [domain.yml](https://github.com/Subrat08/Restaurant_Bot_Rasa/blob/master/domain.yml): This file contains responses that our bot will respond to the user.
 * [actions.py](https://github.com/Subrat08/Restaurant_Bot_Rasa/blob/master/action.py): this contains all the custom actions, such as searching and displaying the restaurants, sending email, validating the user location etc. Make sure you set email and password to authenticate SMTP server in order to send email to the user with restaurant list.

## Rasa and Python version

Name | Version
------------- | -------------
Rasa  | 2.0.2
Python  | 3.8.3

## Sample Interaction with the bot
![Sample interaction](https://i.ibb.co/gPYSp7C/sneekpeek.png)

## Important Note
Use this code for reference and learning purpose only.
