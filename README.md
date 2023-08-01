# Bus Rapid Transit (BRT) Ticketing System App
    #### Video Demo:  <URL HERE>
#### Description:

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Hosting the Website and App](#technologies-used)
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
## Hosting the Website and App

We used ngrok to host our Flask website and app, making it accessible to the public.

### How to Use ngrok

1. Make sure you have ngrok installed on your machine. You can download it from [ngrok.com](https://ngrok.com/download).

2. Start your Flask app locally by running the following command in the terminal:

3. Open a new terminal window and navigate to the directory where you placed the ngrok executable.

4. Expose your local server to the internet by running the following command, replacing `5000` with the port number on which your Flask app is running:


5. ngrok will provide two forwarding URLs, one using HTTP (http://) and another using HTTPS (https://). Copy one of these URLs for use in accessing your hosted app.

### Accessing the Hosted App

You can access our hosted app using the provided ngrok URL: [https://abc123.ngrok.io](https://abc123.ngrok.io). Enjoy exploring our website and app!


## Screenshots
![BRT Ticketing System](https://github.com/sameer693/qr_ticketing-sys/assets/113182835/9232237b-a554-4bd5-b03a-3a86539012d6)
![BRT Ticketing System](https://github.com/sameer693/qr_ticketing-sys/assets/113182835/eedb3b54-97b5-433e-b31d-eb5d87d45f6d)

