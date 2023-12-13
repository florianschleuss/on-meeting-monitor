# On-Meeting Monitor
This small Python client for Windows is meant as a base to work on. 
It provides an easily extensible foundation for sending MQTT or REST requests to wherever.
Currently it is possible to get the status of Microsoft Teams.
The client is completely local, so no API keys are required. It should be plug and play.

## Getting Started
To test the base functionality you can test the [executable](<./dist/OnMeeting Monitor.exe>) directly.
It will display the detected current state and show what it is doing.

Currently it can detect the following `Teams` states:
```
AVAILABLE
AWAY
BUSY
BERIGHTBACK
OFFLINE
DONOTDISTURB
ONTHEPHONE
INAMEETING
PRESENTING
```

## Creating Automation
Some programming is required to use this client.
The [`update()`](https://github.com/florianschleuss/on-meeting-monitor/blob/7048b0349d66c11a16f46173a0a4d42034ddf88e/omm.py#L153) method is the place to attach anything outgoing to control some LED beacons or something else.

## Future
`Zoom` is one thing i want to add but Teams had prio one.

A `LED Beacon` as an indicator for externals outside the homeoffice doors based on an ESP32 + Battery.

## Inspiration
https://github.com/naztronaut/AIIM

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contribute 
I will accept Pull requests for fixing bugs or adding new features after I've vetted them. Feel free to create pull requests!  