import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

# User variables
discord_webhook_url = ""

# Choose, in seconds, how long to wait before checking parcel status.
# (Setting it too low may invoke a rate limit.)
sleep_interval = 120

# You probably won't need to edit anything below this.




try:
    tracking_number = sys.argv[1]
except IndexError:
    sys.exit("You forgot to enter your tracking number.")

url = "https://tracking.dpd.ie/?deviceType=5&consignmentNumber="+str(tracking_number)

init_webhook = DiscordWebhook(url=discord_webhook_url)
init_embed = DiscordEmbed(title='Hello! Started tracking parcel number: '+str(tracking_number), description='I will post any updates here.\n[GitHub](https://github.com/fullonrager/dpd-ie-discord-tracker)', color=0xd20633)
init_webhook.add_embed(init_embed)
try:
    init_webhook.execute()
except requests.exceptions.MissingSchema:
    sys.exit("You forgot to enter your Discord Webhook URL on line 10.")

os.system('cls' if os.name == 'nt' else 'clear')

page = requests.post(url)
soup = BeautifulSoup(page.content, 'html.parser')

for script in soup(["script", "style"]):
    script.extract()

text = soup.get_text()

# Tidy up html
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)

init_matches = re.findall(r"(.*)\n(.*)\n(\d*/\d*/\d*) at\n(\d*:\d*)", text)

for i in range(len(init_matches)):
    info = init_matches[i][0]
    location = init_matches[i][1]
    date = init_matches[i][2]
    _time = init_matches[i][3]
    i = i+1
    print("Update "+str(i)+": "+info+" at "+location+". Date: "+date+" "+_time)

init_updates = len(init_matches)

while 1==1:
    time.sleep(sleep_interval)

    page = requests.post(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    matches = re.findall(r"(.*)\n(.*)\n(\d*/\d*/\d*) at\n(\d*:\d*)", text)

    if len(matches) > init_updates:
        increase = len(matches) - init_updates
        for i in range(increase):
            num = init_updates + i
            info = matches[num][0]
            location = matches[num][1]
            date = matches[num][2]
            _time = matches[num][3]
            update_num = num + 1
            print("Update "+str(update_num)+": "+info+" at "+location+". Date: "+date+" "+_time)

            webhook = DiscordWebhook(url=discord_webhook_url)
            embed = DiscordEmbed(title=info, description="{}\n{} at {}".format(location, date, _time), color=0xd20633)
            embed.set_footer(text='Consignment: {}'.format(str(tracking_number)))
            webhook.add_embed(embed)
            webhook.execute()
        
        init_updates = init_updates + increase