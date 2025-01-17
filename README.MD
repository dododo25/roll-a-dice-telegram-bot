### Roll a Dice

## Description
This is a source code of a Telegram bot. "Roll a Dice" is a game between two playes where each of them are gonna roll some dice and then the winner is decided.
The winner is defined by the combinations of dices that was thrown during a game. Here is a list of such combinations from the lowest in value to the highest:

Combination|Name
---|---
⚀⚁⚂⚃⚅ | high value
⚁⚁⚃⚄⚅ | pair
⚂⚂⚄⚄⚀ | two pairs
⚂⚂⚂⚃⚄ | trio
⚀⚁⚂⚃⚄ | five high straight
⚁⚂⚃⚄⚅ | six high straight
⚂⚂⚂⚄⚄ | full house
⚃⚃⚃⚃⚀ | four of a kind
⚅⚅⚅⚅⚅ | five of a kind

## How to play
Before you enter a playfield, you must connect with a bot. To do that type a `/start` command into a chat or press a "Start" button. List of all available commands:

Command|Description
---|---
`/start` | Start new interaction with a bot
`/new_game` | Play new game with a bot
`/roll` | Roll a dice and see what combination you have
`/help` | Print a helpful tips
`/quit`| Quit playing
