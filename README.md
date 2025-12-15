# Weather Analysis & Monitoring System

An interactive tool for analyzing historical temperature trends and monitoring current weather anomalies using
OpenWeatherMap API. Built with Python and Streamlit.

- Added an interface for uploading a file with historical data.
- Added an interface for selecting a city (from a dropdown list).
- Added a form for entering the OpenWeatherMap API key. When it is not entered, current weather data should not be
  displayed. If the key is invalid, display an error on the screen (it should return {"cod":401, "message": "Invalid API
  key. Please see https://openweathermap.org/faq#error401 for more info."}).

### Display:

- Added descriptive statistics for the city's historical data.
- A temperature time series with anomalies highlighted.
- Seasonal profiles indicating the mean and standard deviation.

### Installation & Setup

> git clone https://github.com/krasnovdanial/TemperatureAnalysisAndMonitoring.git

> cd TemperatureAnalysisAndMonitoring

> poetry install

> create a `.streamlit/secrets.toml` file

> put your API there

> streamlit run src/app.py