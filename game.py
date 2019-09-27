import json
import time
import pandas as pd
import numpy as np
from players import PLAYERS

np.random.seed(seed=int(time.time()))

class wargame():

    def __init__(self, config_path, epochs=10, rounds_per_epoch=20, 
                 world_population=1000, actors=PLAYERS):
        self.epochs = epochs
        self.rounds_per_epoch = rounds_per_epoch
        self.world_population = world_population
        self.actors = actors
        with open(config_path, "r") as fin:
            self.config = json.load(fin)
        self.actor_names = list(self.config.keys())
        self.results_df = pd.DataFrame(columns=self.actor_names)

    def get_outcomes(self, actor_pairs, pair_actions):
        """Interpret actor actions and produce scores"""
        actor_names = self.actor_names
        outcomes = { a:0 for a in actor_names }

        # Interpret player, opponent actions and assign score
        for i, pair in enumerate(actor_pairs):
            player, opponent = (actor_names[int(pair[0])], 
                                actor_names[int(pair[1])])
            player_action, opponent_action = pair_actions[i]
            if player_action*opponent_action == 1:
                # Both cooperate
                outcomes[player] += 1
                outcomes[opponent] += 1
            elif player_action == opponent_action:
                # Both defect
                outcomes[player] -= 1
                outcomes[opponent] -= 1
            elif player_action == 1:
                # Player cooperates, opponent defects
                outcomes[player] += 0
                outcomes[opponent] += 2
            elif opponent_action == 1:
                # Player defects, opponent cooperates
                outcomes[player] += 2
                outcomes[opponent] += 0

        # Weight scores by population size
        for actor, score in outcomes.items():
            outcomes[actor] = score/(self.config[actor]["population"]
                                     *self.world_population)

        return outcomes

    def run_skirmish(self, participants, last_actions=(None, None)):
        """Run one skirmish of epoch"""
        # Get actors
        player = self.actors[self.actor_names[int(participants[0])]]
        opponent = self.actors[self.actor_names[int(participants[1])]]
        # Get actor actions
        player_action = player(last_opponent_action=last_actions[1])
        opponent_action = opponent(last_opponent_action=last_actions[0])

        return player_action, opponent_action

    def run_epoch(self):
        """Run one epoch of wargame"""
        running_outcomes = pd.Series({ a:0 for a in self.actor_names })
        ordered_actors = []
        for i, name in enumerate(self.actor_names):
            population = int(self.config[name]["population"]
                             *self.world_population)
            ordered_actors += [str(i) for p in range(population)]
        shuffled_actors = np.random.permutation(ordered_actors)

        ordered_actors = pd.Series(ordered_actors)
        shuffled_actors = pd.Series(shuffled_actors)
        actor_pairs = (ordered_actors.str.cat(shuffled_actors, sep=",")
                                     .str.split(","))

        for n in range(self.rounds_per_epoch):
            pair_actions = [self.run_skirmish(p) for p in actor_pairs]
            outcomes = self.get_outcomes(actor_pairs, pair_actions)
            running_outcomes += pd.Series(outcomes)

        self.results_df = self.results_df.append(running_outcomes, ignore_index=True)
        return

    def run(self):
        """Run wargame"""
        for epoch in range(self.epochs):
            self.run_epoch()

        return

if __name__ == "__main__":
    game = wargame("configs/config.json")
    game.run()
    print(game.results_df)
