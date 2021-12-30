# zZoom
Automate Zoom Cloud Meeting joining process + Zoom Cloud Meeting Tools - Selenium powered Zoom Cloud Meeting automation

It's easy! - Provide the Zoom link, date & the time - Run **`zZoom.py`** - Sit back & relax :)

![zZoom_info](https://user-images.githubusercontent.com/77499497/147723585-ecf3e52e-5d19-4b66-b245-8fb487bcf867.png)

## Why zZoom?
---
- Instead of using `PyAutoGUI` to interact with the Zoom Desktop application, here we use `Selenium` & `Geckodriver`.
- There are more cool features than just scheduling and automating the joining process!

## Features
---
- Automatically join Zoom Cloud Meetings at given date & time.
- Automatically suspend/sleep the device at the end of the meeting.
- Generate a log with participants' names & their joining time. [Attendance Log] 
- Leave meeting based on conditions. [Users, Timelimit]
- Free & Open Source

## How to use
---
1. Clone this repository or download as a Zip file.
2. Open `MeetingData.txt` file and add meeting details. [Read 'Meeting Data' Section]
3. Run `zZoom.py` with; 
    ```
    py zZoom.py
    ```
4. Sit back & relax :)

## Meeting Data
---
- *username*:- This will appear in the Zoom participants list.
- *meetingLink*:- Your Zoom meeting link (Ex: https://zoom.us/j/12345678912?pwd=ed43djGF5D0RndrcmdJfrsuN1)
- *startDate*:- Meeting date (Ex: 2021.12.31)
- *startTime*:- Meeting starting time (24hrs format - Ex: 16:30)
- *stopIncomingVideo*:- This will stop incomming video from other participants. Will reduce your data charges. (Yes/No)
- *minimumUsersLimit*:- If the amount of participats are less than this value, the session will be automatically terminate. -- This value is combined with 'waitTime'!
- *waitTime*:- After this time period 'minimumUsersLimit' will be considered. -- Value should be in minutes!
- *sleepSystemOnEnd*:- System will put to sleep/suspend at the end of the meeting. (Yes/No)

## Disclaimer
---
- Use this program only for testing and emergency purposes - Always join your meetings & give attention to the speakers.
- With updates in the Zoom Web services, these scripts might fail in some situations - Use at your own risk!

## License & Copyrights
---
**GNU General Public License v3.0**

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU GPLv3**

Geckodriver is used under the [Mozilla Public License](https://www.mozilla.org/en-US/MPL/2.0/). --
Read More @[GitHub](https://github.com/mozilla/geckodriver)

Zoom, Zoom Cloud Meetings, Zoom Desktop, Zoom Logo are copyrights of © *[Zoom Video Communications, Inc](https://zoom.us/)*.
