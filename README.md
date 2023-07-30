# Bus Rapid Transit (BRT) Ticketing System App
    #### Video Demo:  <URL HERE>
#### Description:
![BRT Ticketing System](app_screenshot.png)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)

- [Screenshots](#screenshots)

## Introduction
The Bus Rapid Transit (BRT) Ticketing System is a web application designed to facilitate a convenient and efficient ticketing process for users of the Bus Rapid Transit system. This application is built on the Flask framework and uses SQLite3 as the database to store user information and ticket details. The app incorporates a QR ticketing system for generating and scanning tickets, making it easy for users to travel without the need for physical tickets.

## Features
1. **User Authentication:**
   - Users can register for a new account or log in using existing credentials. Personal information is securely stored in the SQLite3 database.

2. **RFID Card Service:**
   - Users can avail of a service to obtain an RFID card, which enables faster transactions and smoother boarding processes.

3. **QR Ticket Generation:**
   - Users can generate a new ticket by selecting their current location and destination. The app will generate a unique QR code containing a hash that represents the ticket details. These QR codes are secure and cannot be forged.

4. **QR Code Scanning:**
   - The app includes a QR scanner page that allows users to scan their generated QR tickets using any device with a camera. The integration of JavaScript and Instascan ensures efficient and accurate scanning.

5. **Past Travel History:**
   - Users can view their past travel history, including details of previous trips and tickets used, in the "My History" section of the app.

## Technologies Used
- Flask: A lightweight and powerful web framework for Python.
- SQLite3: A serverless, self-contained SQL database engine used for data storage.
- JavaScript: Used for implementing client-side functionalities, including the QR code scanning feature.
- Instascan: A JavaScript library for QR code scanning.
- HTML and CSS: For designing the user interface of the application.

