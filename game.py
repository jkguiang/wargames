import json
import time
import pandas as pd
import numpy as np
from players import PLAYERS

np.random.seed(seed=int(time.time()))

class wargame():

    def __init__(self, config_path, epochs=10, rounds_per_epoch=100, 
                 world_population=5000, actors=PLAYERS):
        self.epochs = epochs
        self.rounds_per_epoch = rounds_per_epoch
        self.world_population = world_population
        self.actors = actors
        with open(config_path, "r") as fin:
            self.config = json.load(fin)
        self.actor_names = list(self.config.keys())
        self.actor_populations = [self.world_population*a["population"] 
                                  for _, a in self.config.items()]
        self.actor_populations = np.array(self.actor_populations)
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
                outcomes[player] -= 2
                outcomes[opponent] -= 2
            elif player_action == 1:
                # Player cooperates, opponent defects
                outcomes[player] -= 1
                outcomes[opponent] += 2
            elif opponent_action == 1:
                # Player defects, opponent cooperates
                outcomes[player] += 2
                outcomes[opponent] -= 1

        return outcomes

    def run_skirmish(self, participants, last_actions=(None, None)):
        """Run one skirmish of epoch"""
        if last_actions[0] and last_actions[1]:
            last_actions = (int(last_actions[0]), int(last_actions[1]))
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
            population = int(self.actor_populations[i])
            ordered_actors += [str(i) for p in range(population)]
        ordered_actors = pd.Series(ordered_actors)

        # Run skirmish rounds
        last_actions = pd.Series(["" for a in ordered_actors.values])
        for n in range(self.rounds_per_epoch):
            # Shuffle and pair actors/actions
            ordered_actions = ordered_actors.str.cat(last_actions, sep=",")
            shuffled_actions = pd.Series(np.random
                                           .permutation(ordered_actions.values))
            shuffled_actors = shuffled_actions.str[0]
            actor_pairs = ordered_actors.str.cat(shuffled_actors, sep=",")
            # Run skirmishes and get outcomes
            if n == 0:
                actor_pairs = actor_pairs.str.split(",")
                pair_actions = actor_pairs.apply(self.run_skirmish)
            else:
                action_pairs = (ordered_actions.str[-1]
                                               .str.cat(
                                                   shuffled_actions.str[-1], 
                                                   sep=","
                                                ))
                actor_action_pairs = (actor_pairs.str.cat(action_pairs, 
                                                          sep=";")
                                                 .str.split(";"))
                # Split actor pairs into tuples for later use
                actor_pairs = actor_pairs.str.split(",")
                pair_actions = actor_action_pairs.apply(
                                   lambda p: 
                                       self.run_skirmish(
                                           p[0].split(","), 
                                           last_actions=p[-1].split(",")
                                       )
                               )
            # Update actor action history
            last_actions = pd.Series([str(p[0]) for p in pair_actions])
            # Update outcomes
            outcomes = self.get_outcomes(actor_pairs, pair_actions)
            running_outcomes += pd.Series(outcomes)

        # Weight scores by population size
        total_population = np.sum(self.actor_populations)
        for actor, score in running_outcomes.items():
            weight = (1/total_population)
            running_outcomes[actor] = score*weight

        # Update results
        self.results_df = self.results_df.append(running_outcomes, 
                                                 ignore_index=True)
        return

    def run(self):
        """Run wargame"""
        for epoch in range(self.epochs):
            old_actor_populations = self.actor_populations
            self.run_epoch()
            print("Outcomes from epoch {}".format(epoch))
            print(self.results_df.iloc[epoch].values)
            self.actor_populations = (old_actor_populations
                                      +self.results_df.iloc[epoch].values
                                      *10)
            self.actor_populations[self.actor_populations < 0] = 0
            print("Population after epoch {}".format(epoch))
            print(self.actor_populations)

        return

if __name__ == "__main__":
    game = wargame("configs/config.json")
    game.run()
    print("Overall results:")
    print(game.results_df)
