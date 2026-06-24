"""Static action sets for binary to discrete action space wrappers."""

# actions for more complex movement
COMPLEX_MOVEMENT = [
    ['NOOP'],
    ['right'],
    ['right', 'A'],
    ['right', 'B'],
    ['right', 'A', 'up'],
    ['right', 'B', 'up'],
    ['right', 'A', 'B', 'up'],
    ['A'],
    ['B'],
    ['A', 'B'],

    ['left'],
    ['left', 'A'],
    ['left', 'B'],
    ['left', 'A', 'up'],
    ['left', 'B', 'up'],
    ['left', 'A', 'B', 'up'],

    ['down', 'A'],
    ['down', 'B'],
    ['down', 'A', 'B'],
    ['up', 'A'],
    ['up', 'A', 'B'],
]
