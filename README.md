# CLU Bot - A LoR Card Look Up Bot for Discord

## Usage

  * card [NAME OF CARD] - Will return the current card art of the requested card, and both levels if the requested card is a champion
  * reload-cache - Will pull new card definitions from Data Dragon.  Is only runnable by the user configured in the `.env` file right now.  This command is hidden from the in-server help response.

## Current Architecture

Currently, this bot will pull the card data from [Legends of Runterra Data Dragon](https://developer.riotgames.com/docs/lor#data-dragon_core-bundles) and store it into a local Redis instance for quick retrieval and so as not to pummel Data Dragon.  Card Data only updates once or twice a month, so this caching should be sufficient for the moment.  When a card is looked up, the card art URL is pulled from the card info JSON stored in Redis and served back to the discord channel, where Discord will expand the image from CDN.

Later on, this bot will include text descriptions of cards, explanations of keywords, a deck code decoder, etc...