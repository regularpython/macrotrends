import requests


class Bot:
    def __init__(self):
        self.scrper_url = None
        self.response = None

    def load_response_get(self, **kwargs):
        self.response = requests.get(self.scrper_url, **kwargs)


if __name__ == '__main__':
    bot = Bot()
    bot.scrper_url = 'https://www.macrotrends.net/stocks/charts/GM/general-motors/income-statement?freq=A'
    bot.load_response_get()
    print(bot.response.text)
