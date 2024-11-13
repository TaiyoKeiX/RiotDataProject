import dictionary
import riotwatcher
from riotwatcher import LolWatcher, ApiError
import requests
import pandas as pd
import time

# Global Variables
api_key = 'RGAPI-49c7609e-d626-452b-8750-20dfddfb4767'
watcher = LolWatcher(api_key)
my_region = 'na1'
puuids = []
players = dictionary.Dictionary()


def getPlayers():
    return players


def getPlayerFromDictionary(player):
    players.get(player)


def getPlayerNameFromPuuid(puuid):
    me = watcher.summoner.by_puuid(my_region, puuid)
    my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
    soloDuo = my_ranked_stats[0]
    return soloDuo['summonerName']


def getPlayerRankedStatsFromPuuid(puuid):
    me = watcher.summoner.by_puuid(my_region, puuid)
    for i in watcher.league.by_summoner(my_region, me['id']):
        if i['queueType'] == 'RANKED_SOLO_5x5':
            return i


def getPuuid(playerName):
    divided = playerName.split('#')
    playerName = divided[0]
    playerTag = divided[1].rstrip('\n')
    apiUrl = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + playerName + "/" + playerTag + "?api_key=" + api_key
    resp = requests.get(apiUrl)
    return resp.json()['puuid']


def tablerCreation(self):
    for i in puuids:
        players.add(self, tabler.tableInformation(i))


class tabler:

    def tableInformation(puuid):
        tier = getPlayerRankedStatsFromPuuid(puuid)['tier']
        rank = getPlayerRankedStatsFromPuuid(puuid)['rank']
        elo = getPlayerRankedStatsFromPuuid(puuid)['leaguePoints']
        playerStats = [tier, rank, elo, totalElo(tier, rank, elo)]
        print(playerStats)
        return playerStats

    def tableAdder(self, name):
        players.add(name, tabler.tableInformation(self))


def totalElo(tier, division, elo):
    return sortingAlg.rankedTierAssigner(tier) + sortingAlg.divisionAssigner(division, tier) + elo


class sortingAlg:
    def rankedTierAssigner(self):
        if self in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
            return 2800
        elif self == 'DIAMOND':
            return 2400
        elif self == 'EMERALD':
            return 2000
        elif self == 'PLATINUM':
            return 1600
        elif self == 'GOLD':
            return 1200
        elif self == 'SILVER':
            return 800
        elif self == 'BRONZE':
            return 400
        elif self == 'IRON':
            return 0

    def divisionAssigner(self, tier):
        if self == 'I' and tier not in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
            return 300
        elif self == 'II':
            return 200
        elif self == 'III':
            return 100
        elif self == 'IV':
            return 0


def sortingAlgorithm():
    return dict(reversed(sorted(players.items(), key=lambda item: item[1][3])))


def functionality():
    playerNameFile = open("playernames.txt", "r")
    lines = playerNameFile.readlines()
    for j in lines:
        puuids.append(getPuuid(j))
        tabler.tableAdder(getPuuid(j), j)
    return sortingAlgorithm()


def infotoDB():
    playerInformationCSV = open("playerinformation.csv", "w+")
    playerInformationCSV.write("playerName,tier,division,points,totalElo" + '\n')
    functionality()
    playersOrdered = sortingAlgorithm()
    for i in playersOrdered:
        csvEntry = i.rstrip('\n')
        for j in playersOrdered[i]:
            j = str(j)
            csvEntry += ',' + j
        playerInformationCSV.write(csvEntry + '\n')


infotoDB()
