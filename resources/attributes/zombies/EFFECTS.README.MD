For a list of possible effects view object/zombie_effects.py

    Triggers:
        default: activates every frame
        death: activates upon death
        init: activates during __init__
        timer: activates periodically, requires the value "frequency" to be defined

    Values:
        default: takes on whatever value is passed
        format: takes in a string and formats it with zombie as self
        format_eval: takes in a string and formats it with zombie as self, then evaluates it as a statement
        repeat_format_eval: takes in a string and stores it, then formats and evaluates every time the effect is activated

        Options:
            attribute: defines the value as a property of the zombie, allowing it to be accessed elsewhere