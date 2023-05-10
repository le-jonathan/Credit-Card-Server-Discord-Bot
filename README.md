# Project 1: Credit Card Server Discord Bot

## Overview
This project is a Discord bot designed to manage user roles and messages within a credit card server. The bot enforces rules for posting in specific channels, manages the assignment of the Diamond role, and handles the removal of the role based on user activity. The bot also assists with the server's rules channel and the user verification process.

## Features
- **Referral Channel Management**: The bot tracks and enforces a 7-day cooldown period between each user's posts in the referral channel. Users who post more frequently will have their messages deleted, and they will receive a warning message.
- **Diamond Role Management**: The bot manages the Diamond role assignment for users with the Diamond Status role. Users who do not meet the required activity level will have their Diamond role removed.
- **Role-Based Access**: Higher-level users (Level 10 or above) have direct access to the full Diamond Membership.
- **User Verification**: The bot posts a message in the rules channel, and users must react with a checkmark to receive the Verified role.
- **User Interaction**: Users can confirm their understanding of the server rules or ask for help through private messages with the bot. The bot will then assign roles or notify moderators accordingly.
- **Persistent Data Storage**: The bot uses a JSON file to store data related to user messages and roles, ensuring consistency even if the bot goes offline.

## Technologies Used
- Python
- discord.py library

As a Computer Science major at Georgia Tech with a focus on Information Internetworks and Media, this project allowed me to apply my knowledge of Discord bot development and Python programming to create a useful and efficient tool for server management. It was an excellent opportunity to refine my skills and explore new possibilities in the world of online communities and automation.
