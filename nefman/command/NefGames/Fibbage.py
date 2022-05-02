import requests
import random
import pprint
import urllib

import config
import command
import backend
import pipeline
import reaction
from command import NefGame


random.seed()


symbols = {
    'menu': [
        '📕',
        '📗',
        '📘',
        '📙',
        '🐳'
    ]

}

menu = symbols['menu']

class TriviaGame(NefGame.Game):

    def __init__(self, message):
        super().__init__(message)

        url = "https://opentdb.com/api.php?amount=10"
        url = "https://opentdb.com/api.php?amount=10&category=15&difficulty=hard&type=multiple&encode=url3986"
        url = "https://opentdb.com/api.php?amount=10&type=multiple&encode=url3986"

        r = requests.get(url)

        if not r.ok:
            raise RuntimeError(f'{r.status_code} - {r.reason} - {r.text}')

        self.questions = r.json()['results']

        self.question_index = 0
        self.player_index   = 0


    async def start(self):

        if(self.question_index == len(self.questions)):
            print('done')
            return

        self.currentPlayer = self.players[self.player_index % len(self.players)]

        cur = self.questions[self.question_index]
        question = cur['question']

        right = cur['correct_answer']
        wrong = cur['incorrect_answers']

        question = urllib.parse.unquote(question)
        right = urllib.parse.unquote(right)

        for i in range(len(wrong)):
            wrong[i] = urllib.parse.unquote(wrong[i])


        #choices = random.shuffle(

        self.choices = [
            (right, True),
            (wrong[0], False),
            (wrong[1], False),
            (wrong[2], False),
        ]

        random.shuffle(self.choices)


        text = f'{self.currentPlayer.mention}\n{question}\n'

        for i in range(len(self.choices)):
             text += (f'{menu[i]} {self.choices[i][0]}\n')

        message = await backend.sendMessage(self.channel, text)

        reaction.add(message, TriviaAnswerCallback, self)


        for i in range(len(self.choices)):
            await backend.emojiReact(message, menu[i])

async def TriviaAnswerCallback(reaction, user, game, removed=False):

    if(game.currentPlayer != user):
        return False

    if(reaction.emoji in menu):
        index = menu.index(reaction.emoji)

    if(game.choices[index][1]):
        message = await backend.sendMessage(game.channel, "Correct!")
    else:
        message = await backend.sendMessage(game.channel, "_Wrong!_")

    game.question_index += 1
    game.player_index   += 1

    game.start()

    return False



NefGame.append(TriviaGame, "trivia")
#command.append(trivia, 'trivia')
