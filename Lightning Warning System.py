import sys, traceback, os, pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
#from geopy import geocoders
from datetime import datetime
 
#def latlng_to_addr (lat, lng):
  #geocoder = geocoders.googlev3.GoogleV3()
  #try:
    #place, point = geocoder.geocode('%s,%s' % (lat, lng), timeout=60)
    #return place
  #except Exception, e:
    #print str(e) + " ==> lat: " + str(lat) + ", lng: " + str(lng)
    #return "None"
 
#def address (latlng):
  #lat, lng = latlng[0], latlng[1]
  #formatted_address = latlng_to_addr(lat, lng)
  #return str(formatted_address)
options = ['1','2','3','4','5']
def show_Options():
  print
  print "**********************************"
  print "1 = Run the program"
  print "2 = Change loop interval per scan"
  print "3 = Add new alert zone"
  print "4 = Delete alert zone"
  print "5 = Display all alert zones"
  print "**********************************"
  print
  choice = raw_input("Enter choice: ")
  return choice

def timeConversionGMT8 (rawDateTime):
  # Convert GMT+0 to GMT+8
  rawDateTime = str(rawDateTime)
  timeOnly = rawDateTime.split()[1]
  hour = int(timeOnly[0:2])
  hourGMT8 = hour + 8
  
  if (len(str(hourGMT8)) != 2):
    hourGMT8 = "0" + str(hourGMT8)
    
  timeGMT8 = str(hourGMT8) + timeOnly[2:]
  datetimeGMT8 = rawDateTime.split()[0] + " " + timeGMT8
  
  return datetime.strptime(datetimeGMT8, '%d-%m-%Y %H:%M:%S').strftime('%d %B %Y, %H:%M:%S')

def dataExtraction(allDataList, variable):
  #JavaScript Variables: thunderstormforecastMarkers, lightningstrikeMarkers, lightningCCstrikeMarkers, lightningCGstrikeMarkers, lsResult, tsResult
  try:
    driver.execute_script('console.log(window.' + variable + '.length)')
  except Exception, e:
    if (variable == "lsResult"):  
      return allDataList.append("There is NO Lightning Stike.")
    elif (variable == "tsResult"):  
      return allDataList.append("There is NO Thunderstorm.")
    
  console_data = (driver.execute_script('return window.JSConsoleCollector ? window.JSConsoleCollector.pump() : []'))
  if variable == "lsResult":  
    list_Size = console_data[1]['arguments']
  elif variable == "tsResult":
    list_Size = console_data[0]['arguments']
  
  
  for i in range(list_Size[0]):
      eachDataDict = {}
      
      driver.execute_script('console.log(window.' + variable + '[' + str(i) + '])')
      console_data = (driver.execute_script('return window.JSConsoleCollector ? window.JSConsoleCollector.pump() : []'))
      
      #lightning strikes
      if variable == "lsResult":  
        lat = console_data[0]['arguments'][0]['latitude']
        lng = console_data[0]['arguments'][0]['longitude']
        
        if lat >= 1.150000 and lat <= 1.478402 and lng >= 103.600000 and lng <= 104.093056:
          eachDataDict['lat'] = lat
          eachDataDict['lng'] = lng
          #eachDataDict['address'] = address([eachDataDict['lat'], eachDataDict['lng']])
          eachDataDict['type'] = str(console_data[0]['arguments'][0]['type'])
          eachDataDict['time'] = timeConversionGMT8(console_data[0]['arguments'][0]['time'])
          #if "singapore" in eachDataDict['address'].lower() and "malaysia" not in eachDataDict['address'].lower() and "indonesia" not in eachDataDict['address'].lower():
          allDataList.append(eachDataDict) 
      
      #thunderstorms    
      elif variable == "tsResult":
        lat = console_data[0]['arguments'][0]['lattitude']
        lng = console_data[0]['arguments'][0]['longitude']
        
        if lat >= 1.150000 and lat <= 1.478402 and lng >= 103.600000 and lng <= 104.093056:
          eachDataDict['lat'] = lat
          eachDataDict['lng'] = lng
          #eachDataDict['address'] = address([eachDataDict['lat'], eachDataDict['lng']])
          eachDataDict['type'] = "TS"
          #if "singapore" in eachDataDict['address'].lower() and "malaysia" not in eachDataDict['address'].lower() and "indonesia" not in eachDataDict['address'].lower():
          allDataList.append(eachDataDict) 
       
  return allDataList

def loadZone():
  zoneListOfDict = []
  # Getting back the objects:
  with open('zone.pickle') as f:
    try:
      zoneListOfDict = pickle.load(f)
    except EOFError:
      pass  
  return zoneListOfDict

def userInput(theInput, text):
  # Validation user input
  while theInput.isalpha():
    print "Invalid input, please key again."
    theInput = raw_input(text)
  return theInput

loopInterval = 10  #default 10 seconds

choice = show_Options()

while choice in options:
  if choice == "1":
    zoneListOfDict = loadZone()
    try:
      while True:
        chrome_options = Options()
        chrome_options.add_extension('extension-js-console-collector.crx')
        driver = webdriver.Chrome('C:\Python27\Scripts\chromedriver.exe',chrome_options=chrome_options)
        driver.get('http://online.weather.gov.sg/lightning/lightning/lightningalertinformationsystem.jsp')
        
        
        sleep(5)  # wait 5 seconds for the webpage to finish processing javascript
        allDataList = []
        
        #JavaScript Variables: thunderstormforecastMarkers, lightningstrikeMarkers, lightningCCstrikeMarkers, lightningCGstrikeMarkers, lsResult, tsResult
        dataExtraction(allDataList, "lsResult")
        dataExtraction(allDataList, "tsResult")
            
        
        totalSize = sum(isinstance(i, dict) for i in allDataList)
        
        print "*" * 80  
        print
        print "Total Results: ", totalSize
        print "-" * 80
        
        if totalSize == 0 and "There is NO Lightning Stike." not in allDataList:
          allDataList.append("There is NO Lightning Stike.")
          
        for i in allDataList:
            print i
        
        if totalSize > 0 and len(zoneListOfDict) > 0:
          for i in allDataList:
            if type(i) == dict:
              for x in zoneListOfDict:
                if i['lat'] < x['Top Left'][0] and i['lng'] > x['Top Left'][1] and i['lat'] < x['Top Right'][0] and i['lng'] < x['Top Right'][1] and i['lat'] > x['Bottom Left'][0] and i['lng'] > x['Bottom Left'][1] and i['lat'] > x['Bottom Right'][0] and i['lng'] < x['Bottom Right'][1]:
                  
		  #Here you can modify how you want to do with the alert..........................
				  
		  print "!!! LIGHTNING ALERT !!!"
                  print "LOCATION: " + x['Zone Name']
                  print i
                  #driver.execute_script('console.log(playSoundFile("/lightning/images/audio.mp3"))')
          
        #sleep(loopInterval)
        for i in range(loopInterval):
          sys.stdout.write("Updating in %d/%d %s\r" % (i+1,loopInterval,"."*(i+1)))
          sys.stdout.flush()
          sleep(1)
        print
        driver.quit()
        
    except KeyboardInterrupt:
      try:
        os.system("taskkill /im chromedriver.exe /f /t >nul 2>&1")
      except Exception:
        pass
      choice = show_Options()        
      
  elif choice == "2":
    loopInterval = int(userInput(raw_input("Update Interval(in seconds): "), "Update Interval(in seconds): "))
    choice = show_Options()
  
  elif choice == "3":
    zoneListOfDict = loadZone()
    
    name = raw_input("Enter new zone name: ")
    topLeft = map(float, userInput(raw_input("Enter top left of zone (e.g. 1.23,103.12): "), "Enter top left of zone (e.g. 1.23,103.12): ").strip().split(','))
    topRight = map(float,userInput(raw_input("Enter top right of zone (e.g. 1.23,103.12): "), "Enter top right of zone (e.g. 1.23,103.12): ").strip().split(','))
    btmLeft = map(float,userInput(raw_input("Enter bottom left of zone (e.g. 1.23,103.12): "), "Enter bottom left of zone (e.g. 1.23,103.12): ").strip().split(','))
    btmRight = map(float,userInput(raw_input("Enter bottom right of zone (e.g. 1.23,103.12): "), "Enter bottom right of zone (e.g. 1.23,103.12): ").strip().split(','))
    
    if (len(topLeft) == 2 and len(topRight) == 2 and len(btmLeft) == 2 and len(btmRight) == 2):
      zoneListOfDict.append({'Zone Name': name, 'Top Left': topLeft, 'Top Right': topRight, 'Bottom Left': btmLeft, 'Bottom Right': btmRight})
      
      # Saving the objects:
      with open('zone.pickle', 'wb') as f:
        pickle.dump(zoneListOfDict, f)
      
      print "Zone successfully added."
    else:
      print "Zone failed to add."
    choice = show_Options()   
    
  elif choice == "4":
    zoneListOfDict = loadZone()
    if len(zoneListOfDict) > 0:
      choiceNumList = []
      for i in range(len(zoneListOfDict)):
        print str(i+1) + ": " + zoneListOfDict[i]['Zone Name']
        choiceNumList.append(i+1)
        
      userChoice = int(userInput(raw_input("Enter choice to delete ('0' to back): "), "Enter choice to delete ('0' to back): "))
      while userChoice not in choiceNumList:
        if userChoice == 0:
          break
        userChoice = int(userInput(raw_input("Enter choice to delete ('0' to back): "), "Enter choice to delete ('0' to back): "))
      if (userChoice == 0):
        pass
      else:
        zoneListOfDict[:] = [d for d in zoneListOfDict if d.get('Zone Name') != zoneListOfDict[userChoice-1]['Zone Name']]
        # Saving the objects:
        with open('zone.pickle', 'wb') as f:
          pickle.dump(zoneListOfDict, f)    
        print "Zone successfully deleted."
    else:
      print "There is NO Alert Zone."
    
    choice = show_Options() 
    
  elif choice == "5":
    zoneListOfDict = loadZone()
    
    if len(zoneListOfDict) > 0:
      for i in range(len(zoneListOfDict)):
        print "=" * 37 + "Zone " + str(i+1) + "=" * 37
        print " " * 30 + 'Zone Name    : ' + str(zoneListOfDict[i]['Zone Name'])
        print " " * 30 + 'Top Left     : ' + str(zoneListOfDict[i]['Top Left'])
        print " " * 30 + 'Top Right    : ' + str(zoneListOfDict[i]['Top Right'])
        print " " * 30 + 'Bottom Left  : ' + str(zoneListOfDict[i]['Bottom Left'])
        print " " * 30 + 'Bottom Right : ' + str(zoneListOfDict[i]['Bottom Right'])
        print
        
    else:
      print "There is NO Alert Zone."    
    choice = show_Options() 