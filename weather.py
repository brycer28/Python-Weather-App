import sys
import requests
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt

load_dotenv()

#create weather app objectf
class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        # create labels
        self.city_label = QLabel("Enter City: ", self)
        self.city_input = QLineEdit(self)
        self.show_weather_button = QPushButton("Show Weather", self)
        self.temperature_label = QLabel()
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        # set layout manager
        vbox = QVBoxLayout()

        # add components to window
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.show_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        # apply changes
        self.setLayout(vbox)

        # align components vertically
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        # set object names (for simplicity)
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.show_weather_button.setObjectName("show_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        # apply a css stylesheet to vbox
        self.setStyleSheet("""
            QLabel, QPushButton{
               font-family: montserrat;        
            }            
            QLabel#city_label{
                font-size: 40px;
                font-style: italic;
                font-weight: bold;
            }
            QLineEdit#city_input{
                font-size: 40px;               
            }
            QPushButton#show_weather_button{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temperature_label{
                font-size: 75px;
            }
            QLabel#emoji_label{
                font-size: 100px;
                font-family: Segoe UI emoji;        
            }
            QLabel#description_label{
                font-size: 50px;
            }
        """)

        self.show_weather_button.clicked.connect(self.show_weather)

    def show_weather(self):
        API_KEY = os.getenv("API_KEY")
        
        # get city name from textbox and pass to API url
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

        # get response from API and specify results, catch errors if shown
        try:
            response = requests.get(url)
            response.raise_for_status() # raise errors to be caught
            data = response.json()

            # data["cod"] returns the error code - 200 means no errors
            if data["cod"] == 200:
                self.display_weather(data)

        # match HTTP error codes to respective error message
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad Request:\nPlease check input and retry")
                case 401:
                    self.display_error("Unauthorized Request:\nInvalid API Key")
                case 403:
                    self.display_error("Forbidden Request:\nProvided API Key does not have access to requested content")
                case 404:
                    self.display_error("Request Not Found:\nCity not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again at another time")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is unable to process your request - please try again at another time")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from the server")
                case _: #default case
                    self.display_error(f"HTTP Error Occurred:\n{http_error}")
        # catch connection errors
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nPlease check your internet connection and try again")
        # catch timeouts
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out - please try again")
        # catch too many redirect errors
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too Many Redirects:\nEnsure the URL is correct and try again")
        # catch request exceptions
        except requests.exceptions.RequestException as request_error:
            self.display_error(f"Request Error:\n{request_error}")

    # display the error being passed in
    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px")
        self.temperature_label.setText(message)

    # display the weather of the entered city
    def display_weather(self, data):
        # reset font size
        self.temperature_label.setStyleSheet("font-size: 75px")

        # get temperature information
        temperature_kelvin = data["main"]["temp"]
        temperature_fahrenheit = round((temperature_kelvin*9/5) - 459.67)
        weather_description = data["weather"][0]["description"]
        weather_id = data["weather"][0]["id"]

        # update graphics components to display weather information
        self.temperature_label.setText(f"{temperature_fahrenheit}°F")
        self.description_label.setText(weather_description.capitalize())
        self.emoji_label.setText(self.get_weather_emoji(weather_id))

    # return an emoji depending on the given weather id code of entered city
    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif (500 <= weather_id <= 531) and weather_id != 511:
            return "🌧️"
        elif weather_id == 511:
            return "❄️🌧️"
        elif 600 <= weather_id <= 611:
            return "🌨️"
        elif 612 <= weather_id <= 622:
            return "🌨️🌧️"
        elif 701 <= weather_id <= 771:
            return "🌁"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif weather_id == 801 or weather_id == 802:
            return "⛅"
        elif weather_id == 803 or weather_id == 804:
            return "☁️"
        else:
            print("ERROR: NO MATCHING EMOJI FOUND")

#create new application and show
if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec())