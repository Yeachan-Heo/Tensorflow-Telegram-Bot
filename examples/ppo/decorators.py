from functools import wraps
from utils import *
import tensorflow as tf


def get_action_decorator(action_func):
    @wraps(action_func)
    def decorated(self, state):
        state = state.reshape((1, self._vh.state_size))
        prediction = self._policy_net(state)
        action, log_prob = action_func(self, prediction)
        return action, log_prob

    return decorated


def train_policy_net_decorator(train_policy_func):
    @wraps(train_policy_func)
    def decorated(self, transitions, advantages):
        states, old_actions, rewards, next_states, dones, old_log_probs = split_transitions(transitions)
        with tf.GradientTape() as tape:
            prediction = self._policy_net(states)
            new_log_probs = train_policy_func(self, prediction, old_actions)
            ratio = tf.exp(old_log_probs - new_log_probs)
            loss = -tf.clip_by_value(ratio, 1 - self._vh.epsilon, 1 + self._vh.epsilon) * advantages
        grads = tape.gradient(loss, self._policy_net.trainable_variables)
        self.optimizer(self._vh.lr_policy_net).apply_gradients(zip(grads, self._policy_net.trainable_variables))

    return decorated
