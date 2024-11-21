// Learning Finite State Machines

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    State_Locked,
    State_Unlocked,
    Count_State,
} State;

typedef enum {
    Event_Coin,
    Event_Push,
    Count_Event,
} Event;

State const g_transitions[Count_Event][Count_State] = {
    [Event_Coin] = {
        [State_Locked] = State_Unlocked,
        [State_Unlocked] = State_Unlocked,
    },
    [Event_Push] = {
        [State_Locked] = State_Locked,
        [State_Unlocked] = State_Locked,
    },
};

void State_print(State state);

int main()
{
    State currentState = State_Locked;

    char input[20];

    State_print(currentState);
    printf(" > ");
    while (fgets(input, sizeof(input), stdin)) {
        input[strlen(input) - 1] = '\0';

        if (strcmp(input, "push") == 0) {
            currentState = g_transitions[Event_Push][currentState];
        } else if (strcmp(input, "coin") == 0) {
            currentState = g_transitions[Event_Coin][currentState];
        } else {
            puts(input);
            return EXIT_SUCCESS;
        }

        State_print(currentState);
        printf(" > ");
    }

    return EXIT_SUCCESS;
}

void State_print(State state)
{
    char *repr;
    switch (state) {
    case State_Locked: repr = "Locked"; break;
    case State_Unlocked: repr = "Unlocked"; break;
    default: repr = "Unknown";
    }
    printf("%s", repr);
}
