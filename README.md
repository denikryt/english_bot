# Telegram Language Learning Bot

This Telegram bot allows users to learn foreign language words by uploading direct text or by scraping text from Wikipedia pages using a link. The bot separates text by sentences and creates a button for each word from the sentence that the user is working on. By pressing a button, the bot replies with the translation of the word to the user's native language, as well as arrow buttons to add or delete the next and previous words from the sentence to get the translation of the needed word in the phrase context. 

Users can save words in their database for test-games. In the test-game, the bot sends a message with the translation of a relevant-to-learn word from the user's database and "*" characters in the count of the original word's letters. The bot also creates buttons with shuffled word's letters, and the user has to spell the word correctly. Users have three tries and three clues, and the usage of tries and clues affects a word's mark. The word's mark has an effect on the bot's random choice in the test-game to send words that the user is most likely learned worse than others.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
