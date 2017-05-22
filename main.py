#!/usr/bin/env python3

# force not to use X-windows
import matplotlib
matplotlib.use('Agg')

from math import radians, cos, sqrt
from datetime import datetime, timedelta
import xmltodict
import json
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def read_stations():
  stations = {}

  with open('stations.xml') as fd:
    doc = xmltodict.parse(fd.read())
    
  for station in doc['Stations']['Station']:
    if station['Land'] == 'NL':
      stations[station['Code']] = (float(station['Lon']), float(station['Lat']))

  return stations

def read_trains():
  with open('trains.json') as fd:    
    return json.load(fd)['trains']

def dist(lonlat1, lonlat2):
  lon1, lat1, lon2, lat2 = map(radians, [lonlat1[0], lonlat1[1], lonlat2[0], lonlat2[1]])
  x = (lon2 - lon1) * cos(0.5 * (lat2 + lat1))
  y = lat2 - lat1
  return 6371 * sqrt(x*x + y*y)

def interpolate(lonlat1, time1, lonlat2, time2, time):
  assert time1 != time2
  assert time1 <= time and time <= time2
  fraction = (time - time1).total_seconds() / (time2 - time1).total_seconds()
  assert 0 <= fraction and fraction <= 1

  lon1, lat1, lon2, lat2 = [lonlat1[0], lonlat1[1], lonlat2[0], lonlat2[1]]
  return (lon1 + (lon2 - lon1) * fraction, lat1 + (lat2 - lat1) * fraction)

def find_train_lines(trains, stations, cur_time):
  train_positions = []
  for train in trains:
    route = train['route']
    time_from = None
    station_from = None
    time_to = None
    station_to = None
    for time_station in route:
      time = datetime.strptime(time_station['time'], '%Y-%m-%dT%H:%M:%S')
      station = time_station['station']
      if time <= cur_time:
        time_from = time
        station_from = station
      if not time_to and time > cur_time:
        time_to = time
        station_to = station
        break
    if time_to and time_from:
      time1 = max(time_from, cur_time - timedelta(seconds=30))
      time2 = min(time_to, cur_time + timedelta(seconds=30))
      pos1 = interpolate(stations[station_from], time_from, stations[station_to], time_to, time1)
      pos2 = interpolate(stations[station_from], time_from, stations[station_to], time_to, time2)
      train_positions.append((pos1, pos2))

  print('found ' + str(len(train_positions)) + ' trains')
  return train_positions

def draw_map():
  fig = plt.figure(1, figsize=(40, 40), frameon=False, dpi=400)
  
  m = Basemap(
    projection='merc',
    lon_0=5.3, lat_0=52,
    resolution = 'h',
    llcrnrlon=3.4, llcrnrlat=50.5,
    urcrnrlon=7.2, urcrnrlat=53.5)
  
  m.drawcoastlines()
  m.drawcountries()
  m.fillcontinents(color='lightgrey',lake_color='aqua')
  m.drawmapboundary(fill_color='aqua')

  return m

def draw_stations(m, stations):
  for station, lonlat in stations.items():
    x, y = m(lonlat[0], lonlat[1])
    m.plot(x, y, 'ro', markersize=4)

def draw_trains(m, train_lines):
  train_artists = []
  for train_line in train_lines:
    x, y = m([train_line[0][0], train_line[1][0]], [train_line[0][1], train_line[1][1]])
    train_artist, = m.plot(x, y, 'k-', markersize=3, linewidth=3)
    train_artists.append(train_artist)
  return train_artists

time = datetime(2017, 5, 16, 6, 0, 0)
stations = read_stations()
trains = read_trains()

m = draw_map()

for iteration in range(840):
  print('{} iteration at time {}'.format(iteration, time.strftime('%H:%M:%S')))

  train_lines = find_train_lines(trains, stations, time)

  draw_stations(m, stations)
  train_artists = draw_trains(m, train_lines)
  time_label = plt.annotate(time.strftime('%H:%M:%S'), xy=(0.05, 0.95), xycoords='axes fraction', fontsize=40, color='green')
  plt.savefig('traffic_' + time.strftime('%H_%M_%S') + '.png', bbox_inches='tight')

  # remove trains and labels
  for a in train_artists:
    a.remove()
  time_label.remove()
  
  time += timedelta(minutes=1)
