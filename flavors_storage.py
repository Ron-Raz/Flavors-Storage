import csv
import math
import time
import datetime
from KalturaClient import *
from KalturaClient.Plugins.Core import *

config = KalturaConfiguration()
config.serviceUrl = "https://www.kaltura.com/"
client = KalturaClient(config)
ks = client.session.start(
    'admin secret',
    'ron.raz@kaltura.com',
    KalturaSessionType.ADMIN,
    1809631,
    86400,
    'disableentitlement')
client.setKs(ks)

def toUnixTime(year,month):
  x= datetime.datetime(year,month,1)
  return int(time.mktime(x.timetuple()))

def getDateWindow(year,month):
  toMonth= month+1
  toYear= year
  if toMonth>12:
    toMonth= 1
    toYear+= 1
  fromDate= toUnixTime(year,month)
  toDate= toUnixTime(toYear,toMonth)-1
  return (fromDate,toDate)


def addSize(year,month,catIds,flavorParamsId,size):
  global storageMap
  if not year in storageMap.keys():
    storageMap[year]= {}
  if not month in storageMap[year].keys():
    storageMap[year][month]= {}
  if not catIds in storageMap[year][month].keys():
    storageMap[year][month][catIds]= {}
  if not flavorParamsId in storageMap[year][month][catIds].keys():
    storageMap[year][month][catIds][flavorParamsId]= 0
  storageMap[year][month][catIds][flavorParamsId]+= size

# objects

mediaFilter = KalturaMediaEntryFilter()
mediaFilter.orderBy = KalturaMediaEntryOrderBy.CREATED_AT_ASC

catFilter = KalturaCategoryEntryFilter()
catPager = KalturaFilterPager()
catPager.pageSize= 99

flavFilter = KalturaAssetFilter()
flavPager = KalturaFilterPager()

storageMap= {}
catMap= {}
flavMap= {}

mediaPager = KalturaFilterPager()

# get the first year to process

mediaPager.pageIndex = 1
mediaPager.pageSize = 1
result = client.media.list(mediaFilter, mediaPager)
fromYear=datetime.datetime.fromtimestamp(result.getObjects()[0].createdAt).year
mediaPager.pageSize= 99

#
# main loop
#

for year in range(fromYear,datetime.date.today().year+1):

  for month in range(1,13):

    (fromDate,toDate)= getDateWindow(year,month)
    mediaFilter.createdAtLessThanOrEqual = toDate
    mediaFilter.createdAtGreaterThanOrEqual = fromDate

    mediaResult = client.media.list(mediaFilter, mediaPager)
    if mediaResult.totalCount > 0:
      print('%d/%02d %d' % (year,month,mediaResult.totalCount))
      for mediaPageIndex in range(1,math.ceil(mediaResult.totalCount/mediaPager.pageSize)+1):
        mediaPager.pageIndex= mediaPageIndex
        mediaResult = client.media.list(mediaFilter, mediaPager)
        for entry in mediaResult.getObjects():
          curId= entry.id
          # check if it's a live entry
          if hasattr(entry, 'recordedEntryId'):
            curId= None
            if entry.recordedEntryId:
              curId= entry.recordedEntryId
          # continue only if VOD or recorded live
          if curId:
            # get categoryID(s)
            catFilter.entryIdEqual = entry.id
            catResult = client.categoryEntry.list(catFilter, catPager)
            catIds= ''
            for cat in catResult.getObjects():
              catIds+= str(cat.categoryId)+'_'
            catIds= catIds[:-1]
            catMap[catIds]= 1
            # get flavors
            flavFilter.entryIdEqual = entry.id
            flavResult = client.flavorAsset.list(flavFilter, flavPager)
            for flav in flavResult.getObjects():
              if flav.size > 0:
                addSize(year,month,catIds,flav.flavorParamsId,flav.size)
                flavMap[flav.flavorParamsId]= 1

# for categories with only 1 ID - get the name
for i in catMap:
  if i.isnumeric():
    result = client.category.get(int(i))
    catMap[i]= result.name
  else:
    catMap[i]= i

# get flavor names
for i in flavMap:
  result = client.flavorParams.get(i)
  flavMap[i]= result.name

# write csv file
f = open("storage_per_flavor.csv", "w")
sortedFlavs= list(flavMap.keys())
sortedFlavs.sort()
csvHeader= 'YEAR/MONTH,CATEGORY'
for flav in sortedFlavs:
  csvHeader+=','+str(flav)
f.write(csvHeader+'\n')
for year in storageMap:
  for month in storageMap[year]:
    for cat in storageMap[year][month]:
      csvLine='%d/%02d,%s' % (year,month,catMap[cat])
      for flav in sortedFlavs:
        val=''
        if flav in storageMap[year][month][cat]:
          val= storageMap[year][month][cat][flav]
        csvLine+= ','+str(val)
      f.write(csvLine+'\n')
f.close()
print('CSV file written.')