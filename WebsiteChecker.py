from urllib import robotparser


class CheckWebsite:
    def __init__(self, robots_txt_url):
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url(robots_txt_url)
        self.rp.read()

    def check_url(self, url):
        return self.rp.can_fetch("*", url)


if __name__ == '__main__':
    cw = CheckWebsite('https://www.macrotrends.net/robots.txt')
    check = cw.check_url('https://www.macrotrends.net/search/')
    print('Can i scrap this website? ', check)
