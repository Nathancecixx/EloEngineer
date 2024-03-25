# Elo Engineer

### (Discord Bot)

## Introduction

Elo Engineer is a multifaceted Discord bot tailored for competitive gaming communities, providing a suite of tools to enhance interaction and gameplay. From casual chats to intense gaming sessions, Elo Engineer is your go-to bot for an enriched Discord experience.

## Features:
### Commands

#### General
* coinflip | Generates a 50/50 coin flip in chat.
* info | Prints details about the server.

#### Music Bot
* join | Joins the voice channel.
* leave | Leaves the voice channel.
* play | Plays a song from a provided YouTube URL.
* que | Displays the next 3 songs in the queue.
* resume | Resumes the paused song.
* skip | Skips the current song and plays the next one in the queue. 
* stop |  Stops the music playback.

#### GameTacker
* lol | Interfaces with the League Of Legends server's for player stats.
  * stats | Provide a username and receive player stats.

* r6 | Interfaces with the Rainbow Six Siege server's for player stats.
  * stats | Provide a username and receive player stats.
  * ops | Provide a username and receive the top 3 attackers and defenders.
  * 
#### Squad Builder
* squad | Provide the number of teammates and optionally the name of game and create a join able squad in discord.

#### No Category
* help | Shows the command list and usage instructions.

## Getting Started

### Dependencies

* Python3.8 or higher
* [Discord.py](https://github.com/Rapptz/discord.py)
  ```
    # Linux/macOS
      python3 -m pip install -U discord.py
    ```
* Youtube.dl
  ```
    # Linux/macOS
      python3 pip install youtube.dl
    ```
* [siegeapi](https://github.com/CNDRD/siegeapi)
  ```
    # Linux/macOS
       python3 -m pip install -U discord.py

    # Windows
       py -3 -m pip install -U discord.py
    ```
* [Riot-Watcher](https://github.com/pseudonym117/Riot-Watcher)
  ```
       pip install riotwatcher
    ```

### Installing

Clone the project to a local repo:
```
git clone https://github.com/Nathancecixx/EloEngineer
```

### Executing program

navigate to the file which contains main and execute command:
```
Python3 main.py
 ```

### Getting it into your server
* Navigate to the Discord Developer Portal and create a new application.
* Go to the 'Bot' tab and click 'Add Bot'.
* Under the 'OAuth2' tab, select 'URL Generator' to generate your bot's invite link.
* Choose the necessary permissions for your bot (like sending messages, managing channels, etc.).
* Copy the generated URL, open it in your browser, and authorize the bot to join your server.

## Help

In the server, use the *help command to get more information on each command and its usage. For example, *help music will provide detailed instructions for all music-related commands.
  ```
  *help
  ```


## Authors

Contributors names and contact info

* [@Nathan Ceci](https://github.com/Nathancecixx)

## Version History

* 0.2
    * Implemented cogs to allow for a more modular codebase
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

Elo Engineer is licensed under the GNU General Public License Version 3. See the [LICENSE](LICENSE) file in the repository for full details.

## Contact

For support or inquiries, feel free to contact us via [email]().
