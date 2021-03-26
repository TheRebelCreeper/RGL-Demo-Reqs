# RGL Demo Parser
import sys
import pandas as pd
import requests
from lxml import html
from random import randint, seed

def extract_players_from_log(link):
	page_content = requests.get(link)
	tree = html.fromstring(page_content.content)
	blu_profiles = tree.xpath('//td[@class="blu badge"]/../td[@class="log-player-name"]/div/ul/li[8]/a/@href')
	blu_names = tree.xpath('//td[@class="blu badge"]/../td[@class="log-player-name"]/div/a/text()')

	red_profiles = tree.xpath('//td[@class="red badge"]/../td[@class="log-player-name"]/div/ul/li[8]/a/@href')
	red_names = tree.xpath('//td[@class="red badge"]/../td[@class="log-player-name"]/div/a/text()')

	blu_df = pd.DataFrame({'Name': blu_names, 'RGL Profile': blu_profiles})
	blu_df['Team'] = 'Blue'

	red_df = pd.DataFrame({'Name': red_names, 'RGL Profile': red_profiles})
	red_df['Team'] = 'Red'

	players = blu_df.append(red_df)
	players['Log'] = link
	players['Requested'] = 'No'
	players['Collected'] = 'No'
	return players

def get_random_player(players, team, prev):
	df = players[players['Team'] == team]
	player_count = len(df.index)

	while True:
		player_num = randint(0, player_count - 1)
		player = df.iloc[player_num]

		# TODO check player not rolled previous week
		if prev is None or not player_in_last_week(player, prev):
			break

	return player

def player_in_last_week(player, prev):
	df = prev[prev['RGL Profile'] == player['RGL Profile']]
	return not df.empty

def main():
	if len(sys.argv) != 3:
		print('Invalid usage')
		print('Expected usage:', sys.argv[0], '[input_file] [week]')
		exit(1)
	else:
		input_file = sys.argv[1]
		week = int(sys.argv[2])

	output_file = 'week_' + str(week) + '_demos.csv'
	if week > 1:
		prev_week = pd.read_csv('week_' + str(week - 1) + '_demos.csv')
	else:
		prev_week = None

	seed()
	with open(input_file, 'r') as f:
		logs = f.read().strip().split('\n')

	rolled_players = pd.DataFrame()

	for log in logs:
		if '#' in log:
			log = log[0:log.index('#')]
		players = extract_players_from_log(log)
		random_blue = get_random_player(players, 'Blue', prev_week)
		random_red = get_random_player(players, 'Red', prev_week)

		rolled_players = rolled_players.append(random_blue)
		rolled_players = rolled_players.append(random_red)

	rolled_players.set_index('Team').sort_index().to_csv(output_file, columns=['Name', 'RGL Profile', 'Log', 'Requested', 'Collected'])

if __name__ == '__main__':
	main()
