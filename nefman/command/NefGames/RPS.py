
import backend
import reaction
from command import NefGame

menu_symbols = {
    'start':'✅'
}

symbols = {
    'rock':'🌑',
    'paper':'📰',
    'scissors':'✂'
}


class RPSGame(NefGame.Game):

#   def __init__(self, message):
#       super().__init__(message)

    async def start(self):
        self.p1_move = None
        self.p2_move = None

        if(len(self.players) == 1):
            self.player1 = self.players[0]
            self.player2 = self.players[0]
        else:
            self.player1 = self.players[0]
            self.player2 = self.players[1]

        message = await backend.sendMessage(self.channel, f"RPS: {self.player1.display_name} vs. {self.player2.display_name}  ")
        p1_msg  = await backend.sendMessage(self.player1, f"RPS: vs. {self.player2.display_name}")
        p2_msg  = await backend.sendMessage(self.player2, f"RPS: vs. {self.player1.display_name}")

        reaction.add(p1_msg, PrivateMoveCallback, self)
        reaction.add(p2_msg, PrivateMoveCallback, self)

        for s in symbols.values():
            await backend.emojiReact(p1_msg, s)
            await backend.emojiReact(p2_msg, s)



    async def end(self):
        if(self.p1_move == self.p2_move):
            #it's a tie
            await backend.sendMessage(self.channel, f"It's a tie!")
            return

        if(self.p1_move == symbols['rock']):
            if self.p2_move == symbols['scissors']:
                self.winner = self.player1

            elif self.p2_move == symbols['paper']:
                self.winner = self.player2

        elif(self.p1_move == symbols['paper']):
            if self.p2_move == symbols['rock']:
                self.winner = self.player1

            if self.p2_move == symbols['scissors']:
                self.winner = self.player2

        elif(self.p1_move == symbols['scissors']):
            if self.p2_move == symbols['paper']:
                self.winner = self.player2

            if self.p2_move == symbols['rock']:
                self.winner = self.player1

        await backend.sendMessage(self.channel, f"{self.winner.display_name} Wins!")



async def PrivateMoveCallback(reaction, user, game, removed=False):
    print("move!", reaction.emoji)

    print(game.player1, user)
    if(reaction.emoji in symbols.values()):
        print('sym')
        if(user == game.player1):
            print("p1!", reaction.emoji)
            game.p1_move = reaction.emoji
        elif(user == game.player2):
            print("p2!", reaction.emoji)
            game.p2_move = reaction.emoji

        if(game.p1_move and game.p2_move):
            await game.end()

#   elif(reaction.emoji == symbols['start']):
#       print(f'start! {user}')
#       await backend.clearReactions(reaction.message)
#       await game.start()
#       return True


NefGame.append(RPSGame, "rps")
