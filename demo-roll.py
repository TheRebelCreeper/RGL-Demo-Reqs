# RGL Demo Parser
import sys
import pandas as pd
import requests
from lxml import html
from random import randint, seed

OUTPUT_NAME = 'demo-roll.csv'

def extract_players_from_log(link):
	page_content = requests.get(link)
	tree = html.fromstring(page_content.content)
	blu_profiles = tree.xpath('//td[@class="blu badge"]/../td[@class="log-player-name"]/div/ul/li[8]/a/@href')
	blu_names = tree.xpath('//td[@class="blu badge"]/../td[@class="log-player-name"]/div/a/text()')

	red_profiles = tree.xpath('//td[@class="red badge"]/../td[@class="log-player-name"]/div/ul/li[8]/a/@href')
	red_names = tree.xpath('//td[@class="red badge"]/../td[@class="log-player-name"]/div/a/text()')

	blu_df = pd.DataFrame({'Name':blu_names, 'RGL Profile':blu_profiles})
	blu_df['Team'] = 'Blue'

	red_df = pd.DataFrame({'Name':red_names, 'RGL Profile':red_profiles})
	red_df['Team'] = 'Red'

	players = blu_df.append(red_df)
	players['Log'] = link
	return players

def get_random_player(players, team):
	df = players[players['Team'] == team]
	player_count = len(df.index)
	
	while True:
		player_num = randint(0, player_count - 1)
		player = df.iloc[player_num]
		# TODO check player not rolled previous week
		break

	return player
	
def main():
	if len(sys.argv) != 2:
		print('Invalid usage')
		exit(1)
	else:
		input_file = sys.argv[1]

	seed()
	with open(input_file, 'r') as f:
		logs = f.read().strip().split('\n')
		print(logs)

	rolled_players = pd.DataFrame()

	for log in logs:
		if '#' in log:
			log = log[0:log.index('#')]
		players = extract_players_from_log(log)
		random_blue = get_random_player(players, 'Blue')
		random_red = get_random_player(players, 'Red')

		rolled_players = rolled_players.append(random_blue)
		rolled_players = rolled_players.append(random_red)

	rolled_players.set_index('Team').sort_index().to_csv(OUTPUT_NAME, columns=['Name', 'RGL Profile', 'Log'])	

if __name__ == '__main__':
	main()
