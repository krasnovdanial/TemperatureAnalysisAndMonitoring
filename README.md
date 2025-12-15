# Система анализа и мониторинга погоды

### Интерактивный инструмент для анализа исторических температурных трендов и мониторинга текущих погодных аномалий с использованием API OpenWeatherMap. Разработан на Python и Streamlit.

- Добавлен интерфейс для загрузки файла с историческими данными.
- Добавлен интерфейс для выбора города (из выпадающего списка).
- Добавлена форма для ввода API-ключа OpenWeatherMap. Если ключ не введен, данные о текущей погоде не отображаются. Если ключ некорректен, на экран выводится ошибка (возвращается ответ: {"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}).

### Отображение данных:

- Добавлена описательная статистика по историческим данным города.
- Временной ряд температур с выделением аномалий.
- Сезонные профили с указанием среднего значения и стандартного отклонения.

### Установка и настройка

> git clone https://github.com/krasnovdanial/TemperatureAnalysisAndMonitoring.git

> cd TemperatureAnalysisAndMonitoring

> poetry install

> create a `.streamlit/secrets.toml` file

> put your API there

> streamlit run src/app.py