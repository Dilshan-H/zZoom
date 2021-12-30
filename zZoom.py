import time
import sys
import csv
import sched
import datetime
import os
import re
from time import time, sleep, strftime, localtime, strptime, mktime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from urllib.parse import urlparse
import cookies #cookies for Zoom Web session


def write_file(participants):
    """Write attendance data to the disk as a CSV file"""
    try:
        with open("attendance.csv", 'w', encoding='utf-8') as f:
            fields = ['Name', 'Timestamp']
            csvwriter = csv.DictWriter(f, fieldnames=fields)
            for userData in participants:
                csvwriter.writerow(userData)
            print("Data saved successfully!")
    except IOError:
        print("Error occured while writing to the disk")


def suspend_pc(stat):
    """Suspend system - Sleep|Hibernate"""
    if stat.lower() == 'yes':
        print('\n', '*' * 25)
        print("-- Suspending system --")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


def load_meeting_data():
    """Load meeting data from file"""
    try:
        with open("MeetingData.txt", 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            if line[0] == '#' or line.strip() == '':
                continue
            data = line.split('=', 1)
            if data[0].strip() == 'username':
                username = data[1].strip()
            elif data[0].strip() == 'meetingLink':
                meetingLink = data[1].strip()
            elif data[0].strip() == 'startDate':
                startDate = data[1].strip()
            elif data[0].strip() == 'startTime':
                startTime = data[1].strip()
            elif data[0].strip() == 'stopIncomingVideo':
                stopIncomingVideo = data[1].strip()
            elif data[0].strip() == 'minimumUsersLimit':
                minimumUsersLimit = data[1].strip()
            elif data[0].strip() == 'waitTime':
                waitTime = data[1].strip()
            elif data[0].strip() == 'sleepSystemOnEnd':
                sleepSystemOnEnd = data[1].strip()
        
        print("Meeting data successfully imported!")
        return([username, meetingLink, startDate, startTime, stopIncomingVideo,
                minimumUsersLimit, waitTime, sleepSystemOnEnd])
        
    except IOError:
        print("Error occured while reading the file")


def launcher():
    """Match the time & date to launch the joining process"""
    print("Loading meeting data...")
    data = load_meeting_data()
    parsedLink = urlparse(data[1])
    if (not('zoom.us' in parsedLink[1]) or not('zoom.us/j/' in data[1])):
        print("""Seems like a invalid meeting link - Check again!
                \nExample: https://zoom.us/j/12345678912?pwd=ed43djGF5D0RndrcmdJfrsuN1""")
        input('\nPress \'ENTER\' to quit... ')
        sys.exit()

    try:    
        data[1] = data[1].split('?')[0].replace('/j/', '/wc/') + '/join?' + data[1].split('?')[1]
    except:
        print("""Error occured while processing meeting link - Check again!
                \nExample: https://zoom.us/j/12345678912?pwd=ed43djGF5D0RndrcmdJfrsuN1""")
        input('\nPress \'ENTER\' to quit... ')
        sys.exit()

    scheduler1 = sched.scheduler(time, sleep)
    startTime = datetime.datetime.strptime(' '.join(data[2:4]), '%Y-%m-%d %H:%M')
    if startTime < datetime.datetime.now():
        print('Start time is not valid!')
        input('\nPress \'ENTER\' to quit... ')
        sys.exit()
    startTime = strptime(' '.join(data[2:4]), '%Y-%m-%d %H:%M')
    startTime = mktime(startTime)
    task = scheduler1.enterabs(startTime, 1, zZoom_join, [data])
    print(f'Waiting untill -- {data[2]} - {data[3]}\n')
    scheduler1.run()


def check_waiting_room(driver):
    """Check waiting room / meeting status in Zoom meeting"""
    connectCount = 0
    while connectCount < 30:
        meetingStat = driver.title
        isWaitingRoom = driver.find_elements(By.XPATH, "//span[text()='Please wait, the meeting host will let you in soon.']")
        
        if len(isWaitingRoom) != 0 or meetingStat == 'The meeting has not started - Zoom':
            print('Waiting...')
            sleep(10)
            connectCount += 1
        else:
            sleep(10)
            return False
    return True 


def check_audio_stat(driver, timeCount):
    """Manage join audio settings in Zoom meeting"""
    connectCount = 0
    sleep(timeCount)
    muteBtn = driver.find_elements(By.XPATH, "//button[text()='Mute']")
    unmuteBtn = driver.find_elements(By.XPATH, "//button[text()='Unmute']")
    joinAudioBtn = driver.find_elements(By.XPATH, "//button[text()='Join Audio']")
    audioPopup = driver.find_elements(By.XPATH, "//span[text()='Computer Audio']")
    
    if len(audioPopup) != 0:
        return "Popup"
    elif len(joinAudioBtn) != 0:
        joinAudioBtn[0].click()
        return "Popup"
    elif len(muteBtn)!= 0:
        muteBtn[0].click()
        return "Muted"
    elif len(unmuteBtn) != 0:
        return "Unmute"


def zZoom_join(data):
    """Automate the joining process on Zoom meeting (Throuh Browser)"""
    print('=' * 15)
    print('Username: ', data[0])
    print('Minimum Users Limit:', data[5])
    print('Suspend at Meeting End :', data[7])
    print('=' * 15, '\n')
    
    print('Starting the joining process...')

    #fireFoxOptions = webdriver.FirefoxOptions()
    #fireFoxOptions.set_headless()
    #driver = webdriver.Firefox(firefox_options=fireFoxOptions)
    driver = webdriver.Firefox()
    driver.get(data[1])

    for cookie in cookies.manage_cookies(data[0]):
        driver.add_cookie(cookie)

    print("Added Session Cookies")
    print("Refreshing the page...")
    driver.refresh()

    try:
        print("Joining the meeting...")
        print("Checking meeting status...")
        meetingStat = check_waiting_room(driver)
        if meetingStat:
            print("- Waiting [startup] timeout -\nClosing the webdriver...")
            driver.quit()
            suspend_pc(data[7])
        driver.find_elements(By.XPATH, "//button[text()='Join']")[0].click()
        sleep(2)
        isCodeError = driver.find_elements(By.ID, "unlogin-join-form")
        if len(isCodeError) != 0:
            print("Seems like Meeting Passcode is incorrect!")
            print("Closing the webdriver...")
            driver.quit()
            suspend_pc(data[7])
        print("Checking for waiting room | Meeting status")
        isWaiting = check_waiting_room(driver)
        if isWaiting:
            print("- Waiting timeout -\nClosing the webdriver...")
            driver.quit()
            suspend_pc(data[7])
        print("Connecting via computer audio...")
    except:
        print("Error occured while connecting to meeting!")
        driver.quit()
        suspend_pc(data[7])
    
    connectCount = 0
    while connectCount < 6:
        try:
            isRecording = driver.find_elements(By.XPATH, "//div[text()='This meeting is being recorded']")
            if len(isRecording) != 0:
                driver.find_elements(By.XPATH, "//button[text()='Got it']")[0].click()
            sleep(1)
            print("Connecting...")
            currStat = check_audio_stat(driver, 5)
            if currStat == "Unmute":
                print("-- Mic is already muted --")
                break
            elif currStat == "Muted":
                print("-- Mic is now muted --")
                break
            elif currStat == "Popup":
                driver.find_elements(By.XPATH, "//button[text()='Join Audio by Computer']")[0].click()
                check_audio_stat(driver, 2)
            print("Connected via computer audio")
            break
        
        except (IndexError, ElementClickInterceptedException):
            sleep(5)
            connectCount += 1
            print("Please wait...")

    if data[4].lower() == 'yes':
        try:
            sleep(3)
            driver.find_elements(By.XPATH, "//div[text()='More']")[0].click()
            sleep(2)
            driver.find_elements(By.XPATH, "//a[text()='Stop Incoming Video']")[0].click()
            print("Disabled incoming video")
        except:
            print("Error occured while stopping incoming video")

    log_participants(driver, data[5], data[6], data[7])


def log_participants(driver, minUsers=5, waitTime=10, suspendStat='yes'):
    """Log participants' names & timestamps"""
    try:
        print("Logging data...\nSit back & relax... :)")
        participants = []
        driver.find_elements(By.XPATH, "//span[text()='Participants']")[0].click()
        sleep(5)
        waitTime = int(waitTime)
        waitTime *= 60
        nowSecs = 0
        while True:
            try:
                isWaiting = check_waiting_room(driver)
                if isWaiting:
                    print("-- Waiting room timeout --\nClosing the webdriver...")
                    raise Exception

                isEnded = driver.find_elements(By.XPATH, "//div[text()='This meeting has been ended by host']")
                if len(isEnded) != 0:
                    print('-- Host ended the meeting --')
                    raise Exception

                limitExceeded = driver.find_elements(By.XPATH, "//div[text()='This free Zoom meeting has ended']")
                if len(limitExceeded) != 0:
                    print('-- Meeting has ended due to time limit --')
                    raise Exception

                meetingUpgraded = driver.find_elements(By.XPATH, "//div[text()='This meeting has been upgraded by the host and now includes unlimited minutes.']")
                if len(meetingUpgraded) != 0:
                    print('-- Meeting has been upgraded --')
                    driver.find_elements(By.XPATH, "//button[text()='OK']")[0].click()
                
                isRecording = driver.find_elements(By.XPATH, "//div[text()='This meeting is being recorded']")
                if len(isRecording) != 0:
                    driver.find_elements(By.XPATH, "//button[text()='Got it']")[0].click()
                    
                askAudio = driver.find_elements(By.XPATH, "//div[text()='The host would like you to speak']")
                if len(askAudio) != 0:
                    sleep(1)
                    print("=== Host asked to unmute ===")
                    driver.find_elements(By.XPATH, "//button[text()='Stay Muted']")[0].click()
                    print("--- Request rejected ---")
                    
                askVideo = driver.find_elements(By.XPATH, "//div[text()='The host has asked you to start your video']")
                if len(askVideo) != 0:
                    sleep(1)
                    print("=== Host asked to enable video ===")
                    driver.find_elements(By.XPATH, "//button[text()='Later']")[0].click()
                    print("--- Request rejected ---")
                    
                activeUsers = driver.find_elements(By.CLASS_NAME, "participants-item__name-section")
                #print('Users: ', len(activeUsers))
                for user in activeUsers[1:]:
                    tempText = re.findall(r"^<span .*\">(.*)<\/span.*\">(.*)<\/span>", user.get_attribute("innerHTML").strip())
                    uName = tempText[0][0] + tempText[0][1]
                    if not any(participant['Name']==uName for participant in participants):
                        #print('Not Found -- Appending: ', uName)
                        participants.append({'Name':uName, 'Timestamp': strftime("%H:%M:%S", localtime())})
                    #print('Curr Amount: ', len(participants))
                if (len(activeUsers) <= int(minUsers)) and (nowSecs > waitTime):
                    print("Minimum users amount reached. -- Leaving from meeting...")
                    write_file(participants)
                    driver.quit()
                    suspend_pc(suspendStat)
                sleep(10)
                nowSecs += 10
            except:
                print('Seems like session has been ended')
                write_file(participants)
                break
        driver.quit()
        suspend_pc(suspendStat)
    except:
        print('-'*25)
        write_file(participants)
        driver.quit()
        suspend_pc(suspendStat)


if __name__ == '__main__':
    launcher()
